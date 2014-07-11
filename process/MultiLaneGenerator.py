"""
 This module is responsible for outputting multilane boudaries
 output is (x, y, z, lanenum)

"""
import numpy as np
from sklearn import cluster
from scipy.spatial import distance, KDTree
import random
from scipy.interpolate import UnivariateSpline
import warnings

"""
returns an m x 3 array of shifted interpolated points
"""
def OffsetInterpolated(lidar, guessInterpolatedLane):
    from scipy.spatial import cKDTree
    #keep the first three coordinates
    guessInterpolatedLane = guessInterpolatedLane[:, :3]
    lidar = lidar[:,:3]
    #setup kd tree, query the nearest interpolated point for each lidar point, and shift by median of the difference
    kdi = cKDTree(guessInterpolatedLane)
    indices = kdi.query(lidar, eps = 0)[1]
    closestInterpolatedPoints = guessInterpolatedLane[indices, :] #indices[1] returns the in
    offset = np.median(closestInterpolatedPoints - lidar, axis = 0)
    shiftedInterpolated = guessInterpolatedLane - offset
    return shiftedInterpolated

class MultiLane:

    def __init__(self, filteredLidarFile, interpolationFile,
                 leftLanes, rightLanes):
        """ 
        Args:
        filteredLidarFile: A .npz file generated by MapBuilder. It should have
                 a 'data' and 't' field
        interpolationFile: A .pickle file containing an interpolated 'left' and
                 'right' lane. This is used to find points in adjacent lanes
        leftLanes: The number of left lanes to look for
        rightLanes: The number of right lanes to look for
        """
        self.npz = np.load(filteredLidarFile)
        self.lanes = self.npz['data']
        self.times = self.npz['t']
        self.interp_lanes = None
        self.interp_times = None

        self.interp = np.load(interpolationFile)
        self.leftLanes = leftLanes
        self.rightLanes = rightLanes

    def extrapolateLanes(self):
        """ Performs all steps necessary to find points of interest for lanes """
        self.extendLanes()
        self.filterLaneMarkings()
        self.clusterLanes()
        self.sampleLanes()
        self.interpolateLanes()
        return self.lanes, self.times

    def saveLanes(self, filepath):
        """ Writes the current state of the generator to a file """
        np.savez(filepath, data=self.lanes, t=self.times)

    def clusterLanes(self):
        """Clusters lanes. A cluster is a sphere of at least 10 points within 3
        meters of eachother. cl.fit_predict may take a long time"""
        cl = cluster.DBSCAN(eps=3, min_samples=8)
        labels = cl.fit_predict(self.lanes[:, :3])
        # Only include points that are in a cluster
        mask = labels > -1
        lanes = np.column_stack((self.lanes[mask, :], labels[mask]))
        times = self.times[mask]
        self.lanes = lanes
        self.times = times
        return self.lanes, self.times

    def extendLanes(self):
        """Translates one interpolated lane to lie on other lanes"""
        left = self.interp['left']
        right = self.interp['right']
        lanes = None
        for imod in xrange(self.rightLanes + self.leftLanes):
            i = imod - self.leftLanes
            lanenew = (right - left) * i + right
            if lanes is not None:
                lanes = np.dstack((lanes, lanenew))
            else:
                lanes = lanenew
        self.interp = lanes
        return self.interp

    def filterLaneMarkings(self):
        """Filters markings close to translated interpolated lane points"""
        lastIndex = 0
        numsegs = 200
        multilanedists = np.ones(
            (self.interp.shape[2], self.lanes.shape[0])) * 1000000
        # find the current index somehow
        for segment in xrange(numsegs):
            if segment % (numsegs / 10) == 0:
                print "Segment ", segment, "/", numsegs
            i = int(float(segment) / numsegs * self.interp.shape[0])
            j = int(float(segment + 1) / numsegs * self.interp.shape[0])
            interpSeg = self.interp[i : j, :,:]
            lastInterpSegPoint = np.array([interpSeg[-1, :, 0]]);
            currentIndex = lastIndex + np.argmin(
                distance.cdist(lastInterpSegPoint, self.lanes[lastIndex:, :3]))
            laneSeg = self.lanes[lastIndex : currentIndex, :];
            for i in xrange(self.interp.shape[2]):
                single = interpSeg[:, :, i]
                singlelanedists = np.min(
                    distance.cdist(laneSeg[:, :3], single[:, :3]), axis=1)
                multilanedists[i, lastIndex:currentIndex] = singlelanedists
            lastIndex = currentIndex
        mins = np.min(multilanedists, axis=0)
        argmins = np.argmin(multilanedists, axis=0)
        # TODO: Why is this hardcoded?
        mask = ((argmins == 0) & (mins < 0.5)) | \
               ((argmins == 1) & (mins < 1.2)) | \
               ((argmins == 2) & (mins < 2.2)) | \
               ((argmins == 3) & (mins < 3.2)) | \
               ((argmins == 4) & (mins < 4.2))
        # mask = ((argmins == 0) & (mins < 0.20)) | \
        #        ((argmins == 1) & (mins < 0.8)) | \
        #        ((argmins == 2) & (mins < 1.2)) | \
        #        ((argmins == 3) & (mins < 2)) | \
        #        ((argmins == 4) & (mins < 2.5))
        filtered = self.lanes[mask]
        filteredargmins = argmins[mask]
        filtered = np.column_stack((filtered, filteredargmins))
        self.lanes = filtered
        self.times = self.times[mask]
        return self.lanes, self.times

    def interpolateLanes(self):
        """Interpolates lane POIs with a univariate spline. """
        # Sort the lane with time information
        # sort_order = np.linalg.norm(lane[:, :3], axis=1).argsort()
        sort_order = self.times.argsort(axis=0)
        self.times = self.times[sort_order]
        self.lanes = self.lanes[sort_order]

        interp_l = np.array([])
        interp_t = np.array([])
        for i in xrange(self.leftLanes + self.rightLanes):
            mask = self.lanes[:, -2] == i
            lane = self.lanes[mask, :]
            times = self.times[mask]

            xinter = UnivariateSpline(times, lane[:, 0], s=0)
            yinter = UnivariateSpline(times, lane[:, 1], s=0)
            zinter = UnivariateSpline(times, lane[:, 2], s=0)
            # 10 points per second
            t = np.arange(times[0], times[-1], 10000)
            a = np.column_stack((xinter(t), yinter(t), zinter(t),
                                 np.ones(t.shape[0]) * i))
            
            # Save the interpolated lane-times and the sorted lane-times
            if interp_l.shape[0] == 0:
                (interp_l, interp_t) = (a, t)
            else:
                (interp_l, interp_t) =  (np.vstack((interp_l, a)), 
                                         np.hstack((interp_t, t)))

        (self.interp_lanes, self.interp_times) = (interp_l, interp_t)
        return self.interp_lanes, self.interp_times

    def sampleLanes(self):
        """ Chooses the median in a cluster """
        l_centroids = []
        t_centroids = []
        for i in np.unique(self.lanes[:, -1]):
            mask = self.lanes[:, -1] == i
            l_cluster = self.lanes[mask]
            t_cluster = self.times[mask]
            l_sample = np.median(l_cluster, axis=0)
            t_sample = np.median(t_cluster, axis=0)
            l_centroids.append(l_sample)
            t_centroids.append(t_sample)
        self.lanes = np.array(l_centroids)
        self.times = np.array(t_centroids)
        return self.lanes, self.times
    
    def fixMissingPoints(self):
        """ This method is not finished yet!! 
        It should remove points that are interpolated for a long distance"""
        for lane in xrange(self.leftLanes + self.rightLanes):
            xyz = self.lanes[self.lanes[:, -2] == lane, :3]
            dist = distance.cdist(xyz, xyz)
            # Don't pick ourselves
            np.fill_diagonal(dist, float('inf'))
            path = []
            idx = []
            for i in xrange(dist.shape[0]):
                # Find the closest point relative to this one
                close_idx = np.argmin(dist[i:, i:], axis=0)[0]
                # Update the relative position to be absolute
                close_idx += i
                # x1, y1, z1, x2, y2, z2, distance
                path.append(np.hstack((xyz[i, :3], xyz[close_idx, :3],
                                       dist[close_idx, i])))
                idx.append(close_idx)
            print np.sort(np.array(idx)) - np.array(idx)
            idx = []
        return np.array(path)
        
        

if __name__ == '__main__':
    warnings.filterwarnings("ignore")  # filtering warnings
    multiLane = MultiLane('/Users/Phoenix/pranav/files/multilanefiles/lanesraw2.npz',
                          '/Users/Phoenix/pranav/files/singlelanefiles/interpolated.pickle',
                          1, 2)
    multiLane.extrapolateLanes()
    multiLane.saveLanes('/Users/Phoenix/pranav/files/multilanefiles/lanesInterpolated3.npy')
