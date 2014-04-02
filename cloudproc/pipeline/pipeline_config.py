import os
from os.path import dirname, join as pjoin
import multiprocessing

CLOUDPROC_PATH = dirname(dirname(os.path.abspath(__file__)))
SAIL_CAR_LOG_PATH = dirname(CLOUDPROC_PATH)

NUM_CPUS = multiprocessing.cpu_count() - 1

DATA_DIR = '/media/sdb'

DSET = '280N_a2'
DSET_DIR = pjoin(DATA_DIR, DSET)

LDR_DIR = pjoin(DSET_DIR, '%s_frames' % DSET[:-1])
POINTS_H5_DIR = pjoin(DSET_DIR, 'h5')
PCD_DIR = pjoin(DSET_DIR, 'pcd')
PCD_DOWNSAMPLED_DIR = pjoin(DSET_DIR, 'pcd_downsampled')
PCD_DOWNSAMPLED_NORMALS_DIR = pjoin(DSET_DIR, 'pcd_downsampled_normals')

DOWNSAMPLE_LEAF_SIZE = 1.0
K_NORM_EST = 30

'''
Print out variable values
'''

if __name__ == '__main__':
    local_vars = locals().copy()
    for k in local_vars:
        if not k.startswith('_') and '<module' not in str(local_vars[k]) and\
                '<function' not in str(local_vars[k]):
            print '{0}: {1}'.format(k, local_vars[k])
