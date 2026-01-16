"""
Modul: raspicar_motors.py
Motor control for the RaspiCar

- Class: Motors
- Methods: run, stop

SLW 27-09-2021
"""

import time
import raspicar_ioctrl

class Motors:
    
    def __init__(self, io):
        self._debug = False
        self._io = io
        self._dir_a, self._dir_b = True, True
        self._io.send_ser("MR0,0")
        self._io.send_ser("MP1,1")
        self._io.send_ser("MD1,1")
        self._mot_a, self._mot_b = 0, 0
        self._mot_power_on = True
        self._cutoff = 20
        # get max speed
        # self._speed_max = int(self._io.send_ser("GM"))
        self._speed_max = 1200   # maximum speed value that can be handled
        # constants for speed and angle calculations
        self._speed_factor, self._turn_factor = round(self._speed_max / 100), 4
        # operating values
        self._mot_stop_cnt = 0
        self._mot_stop_cutoff = 10
        self._lidar_pwr = False
        self._lidar_pwr_cnt = 0
        self._system_end_cnt = 0
        self._system_shutdown_cnt = 0
        self._system_wait = 30
        self._old_buttons = 0
        self._last_cmd = ""
        self._old_button = 0

           
    def run(self, angle: int, speed: int):
        """ Input: x controls rotation angle, range -100 ... +100
                   y controls speed, range -speed_max ... +speed_max
            Shuts motor power off in case there are continously no moves """
        # Calculate speed for motor a and b
        self._mot_a = self._speed_factor * speed - self._turn_factor * angle
        self._mot_b = self._speed_factor * speed + self._turn_factor * angle
        if self._debug:
            print("Mot A:", self._mot_a, "   Mot B:", self._mot_b)
        # Extract turning direction to variables dir_a and dir_b    
        if self._mot_a < 0:
            dir_a = False
            self._mot_a = -self._mot_a
        else:
            dir_a = True
        if self._mot_b < 0:
            dir_b = False
            self._mot_b = -self._mot_b
        else:
            dir_b = True
        # Limit speed to sped_max
        if self._mot_a > self._speed_max:
            self._mot_a = self._speed_max
        if self._mot_b > self._speed_max:
            self._mot_b = self._speed_max
        # Manage the counter for powering off the motors
        if self._mot_a > 0 or self._mot_b > 0:
            if self._mot_stop_cnt >= self._mot_stop_cutoff:
                self._io.send_ser("MP1,1")
            self._mot_stop_cnt = 0
            cmd = "MR" + str(self._mot_a) + "," + str(self._mot_b)
        else:
            cmd = "MR0,0"
            self._mot_stop_cnt += 1
        # Set direction
        if (dir_a != self._dir_a) or (dir_b != self._dir_b):
            dir_cmd = "MD" + ('1' if dir_a else '0') + ',' + ('1' if dir_b else '0')
            self._io.send_ser(dir_cmd)
            if self._debug:
                print(dir_cmd)
            self._dir_a = dir_a
            self._dir_b = dir_b
        # Send speed command
        if cmd != self._last_cmd:
            self._io.send_ser(cmd)
            self._last_cmd = cmd
        # If the power counter reaches its limit, power off the motors
        if self._mot_stop_cnt == self._mot_stop_cutoff:
            self._io.send_ser("MP0,0")
        if self._debug:
            print(cmd)
        
        
    def stop(self):
        self._io.send_ser("MR0,0")
        self._io.send_ser("MP0,0")
        
        
    def set_debug(self, status: bool):
        self._debug = status
        
        
# main =================================================
if __name__ == "__main__":
    
    io = raspicar_ioctrl.IoCtrl()
    time.sleep(0.1)
    mot = Motors(io)
    mot.set_debug(True)
    print()
    
    print("Moving forward ...")
    mot.run(0, +30)
    time.sleep(2)
    mot.run(0, 0)
    time.sleep(1)
    print()
    
    print("Moving backward ...")
    mot.run(0, -30)
    time.sleep(2)
    mot.run(0, 0)
    time.sleep(1)
    print()
    
    print("Turning left ...")
    mot.run(-50, +30)
    time.sleep(2)
    mot.run(0, 0)
    time.sleep(1)
    print()

    print("Turning right ...")
    mot.run(+50, +30)
    time.sleep(2)
    mot.run(0, 0)
    time.sleep(1)
    print()

    mot.stop()
    io.close()
    

            