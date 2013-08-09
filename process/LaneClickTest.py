import sys, os
from GPSReader import *
from VideoReader import *
from WGS84toENU import *
from GPSReprojection import *
from transformations import euler_matrix
from numpy import array, dot, zeros, around, divide, nonzero, float32, maximum
import numpy as np
from cv2 import imshow, waitKey, resize, warpPerspective, getPerspectiveTransform, transpose, Canny, namedWindow
import cv
import cv2
import time
from scipy.io import savemat
from generate_lane_labels import * 


pause_labeler = False
mouse_position = None
left_frames = []
frame_data = []
mouse_click = None

def on_mouse(event, x, y, flags, params):
    global pause_labeler
    global mouse_position
    global mouse_click
    if event == cv.CV_EVENT_LBUTTONDOWN:
        mouse_click = (x, y)
        print mouse_click


if __name__ == '__main__':
  video_filename = sys.argv[1]
  path, vfname = os.path.split(video_filename)
  vidname = vfname.split('.')[0]
  cam_num = int(vidname[-1])
  gps_filename = path + '/' + vidname[0:-1] + '_gps.out'
  out_name = sys.argv[2]

  cv2.namedWindow('video')
  cv.SetMouseCallback('video', on_mouse, 0)
  num_imgs_fwd = 1250; 
  video_reader = VideoReader(video_filename)
  gps_reader = GPSReader(gps_filename)
  gps_dat = gps_reader.getNumericData()

  cam = { }
  cam['R_to_c_from_i'] = array([[-1, 0, 0], \
                         [0, 0, -1], \
                         [0, -1, 0]]);

  if cam_num == 1:
    cam['rot_x'] = deg2rad(-0.8); # better cam 1
    cam['rot_y'] = deg2rad(-0.5);
    cam['rot_z'] = deg2rad(-0.005);
    cam['t_x'] = -0.5;
    cam['t_y'] = 1.1;
    cam['t_z'] = 0.0;
  elif cam_num == 2: 
    cam['rot_x'] = deg2rad(-0.61); # better cam 2 
    cam['rot_y'] = deg2rad(0.2);
    cam['rot_z'] = deg2rad(0.0);
    cam['t_x'] = 0.5;
    cam['t_y'] = 1.1;
    cam['t_z'] = 0.0;

  """
  cam['rot_x'] = deg2rad(-0.66); # cam 1 experimental
  cam['rot_y'] = deg2rad(-0.71);
  cam['rot_z'] = deg2rad(-0.005);
  """
  """
  cam['rot_x'] = deg2rad(-0.62); # cam 2 experimental
  cam['rot_y'] = deg2rad(0.5);
  cam['rot_z'] = deg2rad(0.027);
  """

  cam['fx'] = 2221.8
  cam['fy'] = 2233.7
  cam['cu'] = 623.7
  cam['cv'] = 445.7
  cam['KK'] = array([[cam['fx'], 0.0, cam['cu']], \
                     [0.0, cam['fy'], cam['cv']], \
                     [0.0, 0.0, 1.0]]);

  #framenum = 1926;
  #framenum = 27000
  framenum = 0
  lastTime = time.time()
  lastCols = [None, None]
  lastLine = [None, None, None, None]
  video_reader.setFrame(framenum)

  skip_frame = 10
  default_offset = 60

  src = array([[499,597],[972,597],[1112,661],[448,678]], float32) / 4#good one
  dst = array([[320,320],[960,320],[960,640],[320,640]], float32) / 4
  imsize = (320,240)
  P = getPerspectiveTransform(src,dst)

  while True:
    framenum = framenum + 1;
    (success, I) = video_reader.getNextFrame()
    if success == False:
      break

    if framenum % skip_frame != 0:
      continue

    I = resize(I, imsize)
    WARP = warpPerspective(I, P, imsize);
    
    if lastCols[0] is None:
        M = GPSMask(gps_dat[framenum:framenum+num_imgs_fwd,:], cam, width=1); 
        M = 255 - resize(M, imsize)
        warped_M = np.nonzero(warpPerspective(M, P, imsize))
        col_avg = np.mean(warped_M[1])
        lastCols[0] = col_avg - default_offset
        lastCols[1] = col_avg + default_offset

    if mouse_click is not None:
        col_avg = mouse_click[0] / 2
        dist = min(0.95 * (lastCols[1] - lastCols[0]) / 2, col_avg)
        lastCols[0] = col_avg - dist
        lastCols[1] = col_avg + dist
        print dist
        print lastCols
        mouse_click = None
    
    if lastLine[0] is None:
        lastLine[0] = 0
        lastLine[1] = lastCols[0]
        lastLine[2] = 0
        lastLine[3]= lastCols[1]

   
    I = np.copy(WARP)
    (WARP, lastCols,asdf2) = findLanesConvolution(WARP, (imsize[1], imsize[0]), lastCols, lastLine, frame_rate=skip_frame)
    #(WARP, lastCols,asdf2) = findLanes(WARP, (imsize[1], imsize[0]), lastCols, lastLine, frame_rate=skip_frame)
    line_img = np.zeros((imsize[1], imsize[0]))
    line_img[158:162,:] = 1

    I[WARP[:,:,0] > 0, :] = [0, 0, 255]
    #I[line_img > 0, :] = [255, 0, 0]

    good_img = np.copy(WARP)
    good_img[line_img == 0, : ] = 0
    left_img = np.copy(good_img)
    right_img = np.copy(good_img)
    left_img[:,(lastCols[0]+lastCols[1])/2:,:] = 0
    right_img[:,:(lastCols[0]+lastCols[1])/2,:] = 0
    I[good_img > 0]  = 0
    candidates = np.nonzero(good_img)
    left_candidates = np.nonzero(left_img)
    candidates = np.nonzero(right_img)

    if lastCols[0] is not None and lastCols[1] is not None:
        I[:,lastCols[0],:] = 0
        I[:,lastCols[1],:] = 0
        I[:,(lastCols[0]+lastCols[1])/2,:] = 0

    I = resize(I, (640,480))
    imshow('video',I )
    key = (waitKey(50) & 255)

    if left_candidates[0].size > 0:
        chosen_idx = np.argmax(left_candidates[1])
        point = (left_candidates[1][chosen_idx], left_candidates[0][chosen_idx])
        point_img = np.zeros((imsize[1], imsize[0]))
        point_img[point[1]-2:point[1]+2, point[0]-2:point[0]+2] = 1
        unwarped_img = warpPerspective(point_img, P, imsize, flags=cv.CV_WARP_INVERSE_MAP)
        unwarped_point = np.nonzero(unwarped_img)
        if (len(unwarped_point[0]) > 0):
            unwarped_point = (unwarped_point[1][0] * 4 + 2, unwarped_point[0][0] * 4 + 2)
            left_frames.append(unwarped_point)
        else:
            left_frames.append((-1, -1))
    else:
        left_frames.append((-1, -1))

    if candidates[0].size > 0:
        chosen_idx = np.argmin(candidates[1])
        point = (candidates[1][chosen_idx], candidates[0][chosen_idx])
        point_img = np.zeros((imsize[1],imsize[0]));
        point_img[point[1]-2:point[1]+2, point[0]-2:point[0]+2] = 1
        unwarped_img = warpPerspective(point_img, P, imsize, flags=cv.CV_WARP_INVERSE_MAP)
        unwarped_point = np.nonzero(unwarped_img) 
        if (len(unwarped_point[0]) > 0): 
            unwarped_point = (unwarped_point[1][0]*4 + 2, unwarped_point[0][0]*4 + 2)
            frame_data.append(unwarped_point)
        else:
            frame_data.append((-1,-1))
    else:
        frame_data.append((-1,-1))

    if key == ord('q'):
      break;
    currentTime = time.time();
    if (currentTime - lastTime > 30):
        lastTime = currentTime
        print framenum

  r = np.arange(0,len(frame_data)*skip_frame,skip_frame)
  export_data = -1*np.ones((len(frame_data)*skip_frame+1,2))
  export_data[r,:] = frame_data
  left_data = -1*np.ones((len(left_frames)*skip_frame+1,2))
  left_data[r, :] = left_frames
  savemat(out_name, dict(left=left_data,right=export_data))

