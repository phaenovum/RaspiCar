"""
The process of finding the precise rotation and translation that aligns
the source point cloud to target point cloud in a common coordinate system
is called registration.
"""

import time
import math
import numpy as np
import ydlidar_x2
import raspicar_ioctrl
import raspicar_motors
import matplotlib.pyplot as plt
from lidar_positioning import transform_pc, icp_2d


def start_lidar():
    io.set_lidar_pwr(True)
    lid.connect()
    lid.start_scan()
    time.sleep(1.5)
    
    
def stop_lidar():
    lid.stop_scan()
    time.sleep(0.3)
    lid.disconnect()
    io.set_lidar_pwr(False)
    

def plot_data(ax, xy_data, color='blue', label=''):
    ax.scatter(xy_data[:, 0], xy_data[:, 1], marker='+', color=color, label=label)
    return ax


def plot_car(ax, car, color='black'):
    ax.plot(car[:,0], car[:,1], c=color)
    return ax


def get_data(loops = 3):
    time.sleep(0.5)
    xy = np.empty((0, 2))
    for idx in range(loops):
        while not lid.available:
            time.sleep(0.05)
        xy = np.append(xy, lid.get_xydata(ANGLE_RANGE, 360-ANGLE_RANGE), axis=0)
    return xy


def turn_car(angdgr):
    """ Turns the car by a given number of degrees """
    divider = 21.35
    if angdgr < 0:
        mot.run(-15, 0)
        angdgr = -angdgr
    else:
        mot.run(15, 0)
    time.sleep(angdgr / divider)
    mot.run(0, 0)
    
    
def move_car(y):
    """ Moves the car by a given amount of mm """
    divider = 79.8
    if y < 0:
        mot.run(0, -15)
        y = -y
    else:
        mot.run(0, 15)
    time.sleep(y / divider)
    mot.run(0, 0)
    
    
def match_org(xy_org_front, xy_org_back, limit=1200):
    # limit to data on the left and right side
    xy_org_front_ltd = np.delete(xy_org_front, np.where(abs(xy_org_front[:,1]) > limit), axis=0)
    xy_org_back_ltd = np.delete(xy_org_back, np.where(abs(xy_org_back[:,1]) > limit), axis=0)
    # Estimate rotation angle
    theta_dgr, tx, ty, mean_err, idx = lidpos.icp_2d(xy_org_front_ltd, xy_org_back_ltd,
                                                     angdgr_guess=180, verbose=True)
    xy_org_back = lidpos.transform_pc(xy_org_back, theta_dgr, tx, ty)
    return xy_org_back


#=====================================================================

ANGLE_RANGE = 30

# Initiate modules
io = raspicar_ioctrl.IoCtrl()
time.sleep(0.1)
mot = raspicar_motors.Motors(io)
lid = ydlidar_x2.YDLidarX2()

# Initiate car coordinates
car = np.array([[-70,  150], [  0, 200], [ 70, 150], [ 70, -30],
                [-70,  -30], [-70, 150], [ 70, -30], [-70, -30], [70, 150]])

start_lidar()

# Start graphics
fig, ax = plt.subplots(figsize=(9, 9))

# First position
xy_first = get_data()
ax = plot_data(ax, xy_first, 'blue')
ax = plot_car(ax, car, 'blue')

# Move to second position
move_car(300)
xy_second = get_data()
# Calculate new position
theta_dgr_1, tx_1, ty_1, mean_err, iterations = icp_2d(xy_second, xy_first, verbose=True)
# Transform car and point cloud
xy_second_transformed = transform_pc(xy_second, theta_dgr_1, tx_1, ty_1)
car = transform_pc(car, theta_dgr_1, tx_1, ty_1)
ax = plot_data(ax, xy_second_transformed, 'green')
ax = plot_car(ax, car, 'green')

# Move to third position
turn_car(20)
move_car(300)
xy_third = get_data()
# Calculate new position
theta_dgr_2, tx_2, ty_2, mean_err, iterations = icp_2d(xy_third, xy_second, verbose=True)
# Transform car and point cloud
xy_third_transformed = transform_pc(xy_third, theta_dgr_2, tx_2, ty_2)
xy_third_transformed = transform_pc(xy_third_transformed, theta_dgr_1, tx_1, ty_1)
car = transform_pc(car, theta_dgr_2, tx_2, ty_2)
ax = plot_data(ax, xy_third_transformed, 'red')
ax = plot_car(ax, car, 'red')

# Close motor and LiDAR
mot.stop()
stop_lidar()
time.sleep(0.5)
io.close()

# Show the graphics
plt.show()
