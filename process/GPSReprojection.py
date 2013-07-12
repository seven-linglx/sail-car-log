from transformations import euler_matrix
import numpy as np
from WGS84toENU import *
from numpy import array, dot, zeros, around, divide, ones

def GPSMask(GPSData, Camera): 

    roll_start = -deg2rad(GPSData[0,7]);
    pitch_start = deg2rad(GPSData[0,8]);
    yaw_start = -deg2rad(GPSData[0,9]+90);

    psi = pitch_start; 
    cp = cos(psi);
    sp = sin(psi);
    theta = roll_start;
    ct = cos(theta);
    st = sin(theta);
    gamma = yaw_start;
    cg = cos(gamma);
    sg = sin(gamma);

    R_to_i_from_w = \
            array([[cg*cp-sg*st*sp, -sg*ct, cg*sp+sg*st*cp],
                  [sg*cp+cg*st*sp, cg*ct, sg*sp-cg*st*cp],
                  [-ct*sp, st, ct*cp]]).transpose()


    pts = WGS84toENU(GPSData[0,1:4], GPSData[:,1:4])

    R_to_c_from_i = Camera['R_to_c_from_i']
    R_camera_pitch = euler_matrix(Camera['rot_x'], Camera['rot_y'],\
            Camera['rot_z'], 'sxyz')[0:3,0:3]
    R_to_c_from_i = dot(R_camera_pitch, R_to_c_from_i) 

    #I = zeros((960,1280,3), np.uint8)
    I = 255*ones((960,1280,3), np.uint8)

    world_coordinates = pts;
    pos_wrt_imu = dot(R_to_i_from_w, world_coordinates);
    pos_wrt_camera = dot(R_to_c_from_i, pos_wrt_imu);
    pos_wrt_camera[1,:] += 1.1 #move to ground
    vpix = around(dot(Camera['KK'], divide(pos_wrt_camera, pos_wrt_camera[2,:])))

    for idx in range(1,pts.shape[1]):
      pix = vpix[:,idx]
      if (pix[0] > 0 and pix[0] < 1280 and pix[1] > 0 and pix[1] < 960):
        I[pix[1]-2:pix[1]+2, pix[0]-2:pix[0]+2, 0] = 0;
        I[pix[1]-2:pix[1]+2, pix[0]-2:pix[0]+2, 1] = 0;
        I[pix[1]-2:pix[1]+2, pix[0]-2:pix[0]+2, 2] = 0;
    
    return I

