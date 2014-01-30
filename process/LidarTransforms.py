import numpy as np


def loadLDR(ldrfile):
    dt = [  ('x', np.float32),
                ('y', np.float32),
                ('z', np.float32),
                ('l', np.int16), #intensity
                ('i', np.int16)]; # laser num

    z = np.fromfile(ldrfile, dtype=dt) 
    dat = np.zeros((z.shape[0], 5))
    dat[:,0] = z[:]['x']
    dat[:,1] = z[:]['y']
    dat[:,2] = z[:]['z']
    dat[:,3] = z[:]['i'] 
    dat[:,4] = z[:]['l'] 

    return dat

def loadPCD(pcdfile): 
    f = open(pcdfile, 'r')
    count = 0
    data_started = False
    for l in f:
        t = l.split()
        if t[0] == 'POINTS':
            num_pts = int(t[1])
            pts = np.zeros((num_pts, 4), float)
            continue
        elif t[0] == 'DATA':
            data_started = True
            continue
        elif data_started:
            z = np.array(map(lambda x: float(x), t))
            pts[count,:] = z
            count += 1

    return pts

def R_to_c_from_l(cam):
    # hard coded calibration parameters for now
    R_to_c_from_l = np.array([[0.0, -1.0, 0.0],
                              [0.0, 0.0, -1.0],
                              [1.0, 0.0, 0.0]])

    return R_to_c_from_l


if __name__ == '__main__':
    import sys
    #pts = loadPCD(sys.argv[1])
    pts = loadLDR(sys.argv[1])
    from mpl_toolkits.mplot3d import Axes3D
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.scatter(pts[:,0], pts[:,1], pts[:,2])
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')
    plt.show()