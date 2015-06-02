# usage: 
# python LidarToLRLanesHDR.py <rootdir> <output pickle name>



from Q50_config import *
from ArgParser import *
import sys, os
from GPSReader import *
from GPSTransforms import *
from LidarTransforms import *
from transformations import euler_matrix
import numpy as np
import pickle
import scipy.interpolate
METER_WIN = 30
__all__=['LaneGenerator']

'''
Class that generates initial self-lane boundaries using Lidar maps + GPS track. 
'''
class LaneGenerator():
  '''
  Constructor
  '''
  def __init__(self, rootdir, run_filter = None, targetfolder = '.'):
    self.rootdir = rootdir
    # additional filter that picks a certain run from that day.
    self.run_filter = run_filter
    self.targetfolder = targetfolder
    self.name_offset = len('_gpsmark1.out')



  '''
  Top-level wrapper that does everything.
  '''
  def run(self):
    # iterate all possible sub paths under rootdir, looking for valid files along the way.
    for root, subfolders, files in os.walk(self.rootdir):
      files_day = filter(lambda z: '601.zip' in z, files) 
      if self.run_filter is not None:
        files = filter(lambda z: self.run_filter in z, files_day)
        if len(files_day)==len(files):
          print 'warning: filter '+self.run_filter+' not found in files, including all files.'
      else:
        files = files_day
      print files
      for f in files:
        if not self.setupParams(root,f):
          continue
        self.integrateClouds()
        if not self.interpolatePoints():
          continue
        self.extendLanes()
  

  '''
  Setting up parameters and auxillary data for a particular run
  '''
  def setupParams(self, root,f):
    self.MS_TO_SEC = 1e6
    args = parse_args(root, f+'.avi')
    params = args['params']
    # 50Hz gps data
    gps_name = args['gps_mark1']
    print gps_name
    gps_reader = GPSReader(gps_name)
    GPSData = gps_reader.getNumericData()
    if GPSData.shape[0] ==0:
      print 'empty gps1 log. skipping...'
      return False
    self.imuTransforms = IMUTransforms(GPSData)
    self.GPSTime = utc_from_gps_log_all(GPSData)
    # Video-synced gps data
    gps_name2 = args['gps_mark2']
    gps_reader2 = GPSReader(gps_name2)
    GPSData2 = gps_reader2.getNumericData()
    if GPSData2.shape[0] ==0:
      print 'empty gps2 log. skipping...'
      return False
    self.imuTransforms2 = IMUTransforms(GPSData2)

    # grab the initial time off the gps log and compute start and end times
    self.start_time = self.GPSTime[0] + 1 * self.MS_TO_SEC
    self.end_time = self.GPSTime[0] + 600 * self.MS_TO_SEC
    if self.end_time > self.GPSTime[-1]:
        self.end_time = self.GPSTime[-1]
    self.step_time = 0.5
    self.scan_window = 0.1
    self.dist_window = 5
    self.lidar_loader = LDRLoader(args['frames'])       
    self.T_from_l_to_i = params['lidar']['T_from_l_to_i']
    self.lidar_height = params['lidar']['height']

    print 'gps: '+gps_name
    map_name = gps_name[0:-self.name_offset]+'.map'
    print 'map: '+ map_name
    print self.targetfolder
    self.map_outname = os.path.join(self.targetfolder, (gps_name[0:-self.name_offset]+'_lidarmap.pickle')) 
    self.lane_outname = os.path.join(self.targetfolder, (gps_name[0:-self.name_offset]+'_interp_lanes.pickle')) 
    self.multilane_outname = os.path.join(self.targetfolder, (gps_name[0:-self.name_offset]+'_multilane_points')) 
    print 'out: '+ self.lane_outname
    if os.path.isfile(self.lane_outname):
      print self.lane_outname+' already exists, skipping...'
      return False
    total_num_frames = GPSData.shape[0]
    
    velocities = GPSData[:,4:7]
    velocities[:,[0, 1]] = velocities[:,[1, 0]]
    self.velocities = velocities
    vel_start = ENU2IMUQ50(np.transpose(velocities), GPSData[0,:])
    ## sideways vector wrt starting imu frame
    #sideways_start = np.cross(vel_start.transpose(), self.imuTransforms[:,0:3,2], axisa=1, axisb=1, axisc=1) 
    #self.sideways = sideways_start/(np.sqrt((sideways_start ** 2).sum(1))[...,np.newaxis]) # normalize to unit vector
    # initialize empty data holders
    self.left_data = [ ] 
    self.right_data = [ ] 
    self.left_time = [ ] 
    self.right_time = [ ]
    self.all_data = dict()
    self.all_time = dict()
    self.num_left = 4
    self.num_right = 4
    self.min_width = 3
    self.max_width = 6
    return True

  '''
  Gather points in the left and right borders of the self-lane using heuristic filters.
  '''
  def integrateClouds(self):
    print 'intergrating clouds...'
    current_time = self.start_time
    while current_time + self.scan_window < self.end_time-3e6*self.scan_window:
        print 'Time stamp: '+str(int(current_time))+'/'+str(int(self.end_time))
        # find closest gps timestamp, load from nearby points.
        gps_idx = np.argmin(np.abs(self.GPSTime - current_time))
        backward_near_idx = np.where(np.abs(self.imuTransforms[:gps_idx,:3,3] - self.imuTransforms[gps_idx,:3,3])>=self.dist_window)
        if backward_near_idx is not None and len(backward_near_idx[0])>0:
          backward_near_idx = backward_near_idx[0][-1]+1 # latest past timestamp that is out of dist window range
        else:
          backward_near_idx = gps_idx
        forward_near_idx = np.where(np.abs(self.imuTransforms[gps_idx:-1,:3,3] - self.imuTransforms[gps_idx,:3,3])>=self.dist_window)
        if forward_near_idx is not None and len(forward_near_idx[0])>0:
          forward_near_idx = gps_idx + forward_near_idx[0][0] # first future timestamp that is out of dist window range
        else:
          forward_near_idx = gps_idx+1
        if forward_near_idx-backward_near_idx>1:
          #near_time = self.GPSTime[backward_near_idx:forward_near_idx]
          #scan_window = max(self.scan_window, (np.max(near_time)-np.min(near_time))/2e6)
          data1, t_data1 = self.lidar_loader.loadLDRWindow(self.GPSTime[backward_near_idx],self.scan_window)
          data2, t_data2 = self.lidar_loader.loadLDRWindow(self.GPSTime[forward_near_idx],self.scan_window)
          if data1 is None:
            data = data2
            t_data = t_data2
          else:
            if data2 is None:
              data = data1
              t_data = t_data1
            else:
              data = np.concatenate((data1,data2),axis=0)
              t_data = np.concatenate((t_data1,t_data2),axis=0)
        else:
          # load points w.r.t lidar at current time
          data, t_data = self.lidar_loader.loadLDRWindow(current_time,self.scan_window)
        if data is None or data.shape[0]==0:
          current_time += self.step_time * self.MS_TO_SEC
          continue
        dist = np.sqrt(np.sum( data[:, 0:3] ** 2, axis = 1))
        # distance filters, intensity filter, height filter.
        data_filter_mask = (dist > 3)                  & \
                           (dist < 8)                  & \
                           (data[:,3] > 35)            & \
                           (data[:,2] < -(self.lidar_height-0.05))          & \
                           (data[:,2] > -(self.lidar_height+0.05))          
        left_mask = data_filter_mask & (data[:,1] < 2.2) & (data[:,1] > 1.2)  # left lane filter
        right_mask = data_filter_mask & (data[:,1] > -2.2) & (data[:,1] < -1.2)  # right lane filter
        left = data[left_mask, :]
        right = data[right_mask, :]
        left_t = t_data[left_mask]
        right_t = t_data[right_mask]
        
        # transform data into IMU frame at time t
        lpts = left[:,0:3].transpose()
        lpts = np.vstack((lpts,np.ones((1,lpts.shape[1]))))
        lpts = np.dot(self.T_from_l_to_i, lpts)

        # transform data into imu_0 frame
        lpts = transform_points_by_times(lpts, left_t, self.imuTransforms, self.GPSTime)
        lpts = lpts.transpose()

        # for exporting purposes
        lpts_copy = array(lpts[:,0:3])
        lpts_copy = np.column_stack((lpts_copy, array(left[:,3])))
        self.left_data.append(lpts_copy)
        self.left_time.append(np.reshape(left_t, [len(left_t),1]))
        


        # transform data into IMU frame at time t
        rpts = right[:,0:3].transpose()
        rpts = np.vstack((rpts,np.ones((1,rpts.shape[1]))))
        rpts = np.dot(self.T_from_l_to_i, rpts)
        # transform data into imu_0 frame
        rpts = transform_points_by_times(rpts, right_t, self.imuTransforms, self.GPSTime)
        rpts = rpts.transpose()

        # for exporting purposes
        rpts_copy = array(rpts[:,0:3])
        rpts_copy = np.column_stack((rpts_copy, array(right[:,3])))
        self.right_data.append(rpts_copy)
        self.right_time.append(np.reshape(right_t, [len(right_t),1]))
        current_time += self.step_time * self.MS_TO_SEC

        self.all_data['left'] = np.row_stack(self.left_data)
        self.all_data['right'] = np.row_stack(self.right_data)
        self.all_time['left'] = np.row_stack(self.left_time)
        self.all_time['right'] = np.row_stack(self.right_time)
    print 'saving lidar map to '+self.map_outname
    savefid1 = open(self.map_outname,'w')
    pickle.dump(self.all_data, savefid1)
    savefid1.close()
    print 'done'

  '''
  Given the points in the left and right lanes borders, interpolate them 
  into smooth curves by taking reference to the car's trajectory.
  '''
  def interpolatePoints(self):
    subsample_dist = 0.5
    left_data = self.all_data['left']
    right_data = self.all_data['right']
    left_t = self.all_time['left']
    right_t = self.all_time['right']
    print left_data.shape
    print right_data.shape
    height_array = np.zeros([3,3])
    height_array[2,0]=-self.lidar_height
    down_vec = np.dot(self.imuTransforms[:,0:3,0:3], height_array)[:,:,0] # shift down in the self frame
    self.imuTransforms[1:,0:3,3] += down_vec[1:,:] # don't shift the 0th frame otherwise will mess up. Only do that later.
    # remove timestamps that is too slow.
    #self.imuTransforms = self.imuTransforms[np.where(np.sqrt((self.velocities ** 2).sum(-1))>0.05),:,:]
    subsample_idx = [0] # always include the first frame
    for i in range(self.imuTransforms.shape[0]):
      if np.dot(np.linalg.inv(self.imuTransforms[subsample_idx[-1],:,:]), self.imuTransforms[i,:,:])[0,3]>subsample_dist:
        subsample_idx.append(i)
    self.imuTransforms = self.imuTransforms[subsample_idx,:,:] 
    vel_start = self.imuTransforms[1:,0:3,3] - self.imuTransforms[0:-1,0:3,3]
    print vel_start.shape
    print self.imuTransforms[0:-1,0:3,2].shape
    sideways_start = np.cross(vel_start, self.imuTransforms[0:-1,0:3,2], axisa=1, axisb=1, axisc=1) 
    self.sideways = sideways_start/(np.sqrt((sideways_start ** 2).sum(1))[...,np.newaxis]) # normalize to unit vector

    # map points are defined w.r.t the IMU position at time 0
    # each entry in map_data is (x,y,z,intensity,framenum). 
    total_num_frames = self.imuTransforms.shape[0]
    print self.imuTransforms.shape
    leftLaneData = np.ones([total_num_frames, 3])*self.MS_TO_SEC
    rightLaneData = np.ones([total_num_frames, 3])*self.MS_TO_SEC
    for frame in xrange(total_num_frames-1):
        if frame%500==0:
          print 'collecting L/R lane pts: '+str(frame)+'/'+str(total_num_frames)
        imuTransforms_t = self.imuTransforms[frame,:,:]
        imu_pos = imuTransforms_t[0,3] # current x position in the 0th imu frame
        # only care within ~ 2 seconds window, so that not likely to have a loop that mess up linear interp
        # also only care about points within ~16 meters from current position
        #mask_window = (left_data[:,4] < frame + FRAME_WIN) & (left_data[:,4] > frame-FRAME_WIN);
        mask_window = (left_data[:,0] < imu_pos + METER_WIN) & (left_data[:,0] > imu_pos-METER_WIN);
        left_data_copy = array(left_data[mask_window, 0:3]);
        if left_data_copy.shape[0]>0:
          # find the 'left lane' point that closest to the current self-position
          l_distances = np.cross(left_data_copy - imuTransforms_t[0:3,3].transpose(), self.sideways[frame,:], axisa=1)
          #l_distances = left_data_copy - imuTransforms_t[0:3,3].transpose()
          #l_angles = np.dot(l_distances, self.sideways[frame,:])
          l_distances = np.sqrt((l_distances ** 2).sum(-1))
          #l_angles = l_angles/l_distances
          #idx = np.argmin(l_distances)
          if np.min(l_distances)<=0.5: #3 and np.abs(l_angles[idx])<0.08: # do nothing if it's too far.
            # compute the relative position of the left lane marking exactly on my side
            leftLaneData[frame,:] = left_data_copy[np.argmin(l_distances),:] - imuTransforms_t[0:3,3]
        
        #mask_window = (right_data[:,4] < frame + FRAME_WIN) & (right_data[:,4] > frame-FRAME_WIN);
        mask_window = (right_data[:,0] < imu_pos + METER_WIN) & (right_data[:,0] > imu_pos-METER_WIN);
        right_data_copy = array(right_data[mask_window, 0:3]);
        if right_data_copy.shape[0]>0:
          # find the 'right lane' point that closest to the current self-position
          r_distances = np.cross(right_data_copy - imuTransforms_t[0:3,3].transpose(), self.sideways[frame,:], axisa=1)
          #r_distances = right_data_copy - imuTransforms_t[0:3,3].transpose()
          #r_angles = np.dot(r_distances, self.sideways[frame,:])
          r_distances = np.sqrt((r_distances ** 2).sum(-1))
          #r_angles = r_angles/r_distances
          idx = np.argmin(r_distances)
          if np.min(r_distances)<=0.5:#3: #and np.abs(r_angles[idx])<0.08:
            # compute the relative position of the right lane marking exactly on my side
            rightLaneData[frame,:] = right_data_copy[np.argmin(r_distances),:] - imuTransforms_t[0:3,3]
   
    
    print 'interpolating...'
    # perform interpolation on the relative positions, then add back to the absolute imu positions
    all_time = np.arange(0, total_num_frames)
    left_time_array = np.where(leftLaneData[:, 0] < 5e5)[0]
    print left_time_array.shape
    right_time_array = np.where(rightLaneData[:, 0] < 5e5 )[0]
    print right_time_array.shape
    if left_time_array.shape[0]==0 or right_time_array.shape[0]==0:
      print 'Warning: not enough points to perform lane interpolation. lane pickle file will not be generated!'
      return False
    polynomial_fit=1
    smoothing = 1
    spline_left_x = scipy.interpolate.UnivariateSpline(left_time_array, leftLaneData[left_time_array, 0], k=polynomial_fit, s=smoothing)
    spline_left_y = scipy.interpolate.UnivariateSpline(left_time_array, leftLaneData[left_time_array, 1], k=polynomial_fit, s=smoothing)
    spline_left_z = scipy.interpolate.UnivariateSpline(left_time_array, leftLaneData[left_time_array, 2], k=polynomial_fit, s=smoothing)
    spline_right_x = scipy.interpolate.UnivariateSpline(right_time_array, rightLaneData[right_time_array, 0],k=polynomial_fit, s=smoothing)
    spline_right_y = scipy.interpolate.UnivariateSpline(right_time_array, rightLaneData[right_time_array, 1],k=polynomial_fit, s=smoothing)
    spline_right_z = scipy.interpolate.UnivariateSpline(right_time_array, rightLaneData[right_time_array, 2],k=polynomial_fit, s=smoothing)

    output_left = np.copy(self.imuTransforms[:,0:3,3]);
    output_left[:,0] += smoothData(spline_left_x(all_time));
    output_left[:,1] += smoothData(spline_left_y(all_time));
    output_left[:,2] += smoothData(spline_left_z(all_time));
    output_left[0,:] += down_vec[0,:] # first frame hasn't been shifted down to ground. do that now.
    

    output_right = np.copy(self.imuTransforms[:,0:3,3]);
    output_right[:,0] += smoothData(spline_right_x(all_time));
    output_right[:,1] += smoothData(spline_right_y(all_time));
    output_right[:,2] += smoothData(spline_right_z(all_time));
    output_right[0,:] += down_vec[0,:]
    # estimate lane width for this run
    lane_diff = np.sqrt(np.sum((output_left-output_right)**2, axis=1))
    self.lane_width = np.mean(lane_diff[np.logical_and(lane_diff<self.max_width,lane_diff>self.min_width)])
    # remove outliers
    left_diff = np.sqrt(np.sum((output_left - self.imuTransforms[:,0:3,3])**2, axis=1))
    self.left_valid_idx = np.where(np.logical_and(left_diff<self.max_width/2.0,left_diff>self.min_width/2.0))[0]
    output_left = output_left[self.left_valid_idx, :]
    # remove outliers
    right_diff = np.sqrt(np.sum((output_right - self.imuTransforms[:,0:3,3])**2, axis=1))
    self.right_valid_idx = np.where(np.logical_and(right_diff<self.max_width/2.0,right_diff>self.min_width/2.0))[0]
    output_right = output_right[self.right_valid_idx, :]
    
    self.interp = dict()
    self.interp['left']=output_left
    self.interp['right']=output_right
    print 'valid output size: '+str(output_left.shape[0])+'   '+str(output_right.shape[0]) 
    savefid = open(self.lane_outname,'w')
    pickle.dump(self.interp, savefid)
    savefid.close()
    return True

  def extendLanes(self):
    """Translates one interpolated lane to lie on other lanes"""
    left = self.interp['left']
    right = self.interp['right']
    out = {}
    num_lanes = self.num_left + self.num_right
    out['num_lanes'] = np.array(num_lanes)
    out['num_left'] = np.array(self.num_left)
    out['num_right'] = np.array(self.num_right)
    lanes = None
    lane_cnt=0
    print 'Estimated lane width: '+str(self.lane_width)+' meters'
    # shift the left lane left
    for i in range(self.num_left):
      lanenew = left[0:-1] - self.sideways[self.left_valid_idx[0:-1]] * self.lane_width * i
      out['lane' + str(lane_cnt)] = lanenew
      lane_cnt+=1
    # shift the right lane right
    for i in range(self.num_right):
      lanenew = right[0:-1] + self.sideways[self.right_valid_idx[0:-1]] * self.lane_width * i
      out['lane' + str(lane_cnt)] = lanenew
      lane_cnt+=1
    assert lane_cnt==num_lanes
    print 'Saving', self.multilane_outname
    np.savez(self.multilane_outname, **out)



if __name__ == '__main__': 
    rootdir = sys.argv[1]
    if rootdir[-1]=='/':
      rootdir = rootdir[0:-1] # remove trailing '/'
    path, directory = os.path.split(rootdir)
    run_filter = None
    if len(sys.argv)>2:
      run_filter=sys.argv[2]
    targetfolder = '/scail/group/deeplearning/driving_data/640x480_Q50/' + directory + '/'
    #targetfolder = '/deep/group/driving/driving_data/jkiske/single_lanes/' + directory + '/'
    lane_generator = LaneGenerator(rootdir, run_filter=run_filter, targetfolder = targetfolder)
    lane_generator.run()
