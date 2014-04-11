import os
from os.path import dirname, join as pjoin
import multiprocessing

CLOUDPROC_PATH = dirname(dirname(os.path.abspath(__file__)))
SAIL_CAR_LOG_PATH = dirname(CLOUDPROC_PATH)

NUM_CPUS = multiprocessing.cpu_count() - 1

DATA_DIR = '/media/sdb'

DSET = '17N_b2'
DSET_DIR = pjoin(DATA_DIR, DSET)
DSET_AVI = DSET + '.avi'
CAM_NUM = int(DSET[-1])

# Stuff to scp over
# TODO Add command for running generate_frames_and_map to pipeline
REMOTE_DATA_DIR = 'robo:/scail/group/deeplearning/driving_data/sameep/4-2-14-monterey'
REMOTE_FILES = [
    'split_\\*_%s.avi' % DSET,
    #'%s_gps.out' % DSET[:-1],
    #'%s_frames' % DSET[:-1],
    #'%s.map' % DSET[:-1],
    '%s_*.bag' % DSET[:-1],
    '%s.pcap' % DSET[:-1],
    'params.ini'
]

PARAMS_FILE = pjoin(DSET_DIR, 'params.ini')
GPS_FILE = pjoin(DSET_DIR, '%s_gps.out' % DSET[:-1])
MAP_FILE = pjoin(DSET_DIR, '%s.map' % DSET[:-1])

PARAMS_H5_FILE = pjoin(DSET_DIR, 'params.h5')
LDR_DIR = pjoin(DSET_DIR, '%s_frames' % DSET[:-1])
POINTS_H5_DIR = pjoin(DSET_DIR, 'h5')
PCD_DIR = pjoin(DSET_DIR, 'pcd')
PCD_DOWNSAMPLED_DIR = pjoin(DSET_DIR, 'pcd_downsampled')
PCD_DOWNSAMPLED_NORMALS_DIR = pjoin(DSET_DIR, 'pcd_downsampled_normals')
ICP_TRANSFORMS_DIR = pjoin(DSET_DIR, 'icp_transforms')
COLOR_DIR = pjoin(DSET_DIR, 'color')
COLOR_CLOUDS_DIR = pjoin(DSET_DIR, 'color_clouds')
MERGED_CLOUDS_DIR = pjoin(DSET_DIR, 'merged_clouds')
OCTOMAP_DIR = pjoin(DSET_DIR, 'octomaps')

EXPORT_FULL = False
LANE_FILTER = False
EXPORT_START = 5800
EXPORT_NUM = 200
EXPORT_STEP = 5

DOWNSAMPLE_LEAF_SIZE = 1.0
K_NORM_EST = 30

ICP_ITERS = 20
# NOTE set this parameter based on GPS delta spikes,
# downsampling voxel leaf size, and time steps between scans
ICP_MAX_DIST = 5.0

LIDAR_PROJECT_MIN_DIST = 3.0

CLOUD_MAX_STORE = 200
MAP_COLOR_WINDOW = 25

OCTOMAP_RES = 0.5
OCTOMAP_FILE = '{0}/octomap_{1:.2f}.bt'.format(OCTOMAP_DIR, OCTOMAP_RES)

'''
Print out variable values
'''

if __name__ == '__main__':
    local_vars = locals().copy()
    for k in local_vars:
        if not k.startswith('_') and '<module' not in str(local_vars[k]) and\
                '<function' not in str(local_vars[k]):
            print '{0}: {1}'.format(k, local_vars[k])
