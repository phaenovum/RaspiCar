#!/usr/bin/
"""
RaspiCar - run_straight.py

Drives forward until it finds an obstacle,
then turns around by approximately 180 degrees
There are 2 speed modes set depending on the distances:
fast_speed for longer distances and slow_speed for short distances

SLW 10-01-2026
Last update: -
"""

import os
import time
import ydlidar_x2
import raspicar_ioctrl
import raspicar_motors
import raspicar_camera

# Initialize objects
io = raspicar_ioctrl.IoCtrl()
mot = raspicar_motors.Motors(io)
lid = ydlidar_x2.YDLidarX2()
cam = raspicar_camera.Camera()

# Start the LiDAR
io.set_lidar_pwr(True)
lid.connect()
lid.start_scan()
time.sleep(0.3)

# Start the camera
cam.show_frame()

# Drive forward until there is an obstacle on sectors20[9, 10]
fast_speed, slow_speed = 40, 10
speed = slow_speed
mot.run(0, speed)
        
while True:
    sectors = lid.get_sectors20()
    distance = sectors[8:12]
    distance[distance <= 10] = 9999  # Replace missing values with a large number
    min_distance = distance.min()
    print(distance, min_distance)
    if min_distance < 150:
        print("Halting motors")
        # Stop motors
        mot.run(0, 0)
        break
    elif min_distance < 300:
        if speed > slow_speed:
            print("Reducing speed")
            speed = slow_speed
            mot.run(0, speed)
    else:
        if speed < fast_speed:
            print("Increasing speed")
            speed = fast_speed
            mot.run(0, speed)

    cam.show_frame()
    time.sleep(0.1)
    
# Stop LiDAR
lid.stop_scan()
lid.disconnect()
io.set_lidar_pwr(False)

# Turn around
mot.run(50, 0)
time.sleep(2.5)

# Close everything
mot.stop()
cam.close()
io.close()
print("Done")
