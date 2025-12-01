"""
Modul: raspicar_motors.py
Motor control for the RaspiCar

- Class: Motors
- Methods: run, stop

SLW 27-09-2021
"""

import time
import raspicar_ioctrl

debug = False

class Motors:
    
    def __init__(self, io):
        self._io = io
        self._dir_a, self._dir_b = True, True
        self._io.send_ser("MR0,0")
        self._io.send_ser("MP1,1")
        self._io.send_ser("MD1,1")
        self._mot_a, self._mot_b = 0, 0
        self._mot_power_on = True
        self._cutoff = 20
        # constants for speed and angle calculations
        self._speed_factor, self._turn_factor = 15, 4
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

           
    def run(self, angle, speed):
        """ Input: x controls rotation angle, range -100 to +100
                   y controls speed, range -1000 to +1000.
            Shuts motor power off in case there are continously no moves """
        self._mot_a = self._speed_factor * speed - self._turn_factor * angle
        self._mot_b = self._speed_factor * speed + self._turn_factor * angle
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
        if self._mot_a > 0 or self._mot_b > 0:
            if self._mot_stop_cnt >= self._mot_stop_cutoff:
                self._io.send_ser("MP1,1")
            self._mot_stop_cnt = 0
            cmd = "MR" + str(self._mot_a) + "," + str(self._mot_b)
        else:
            cmd = "MR0,0"
            self._mot_stop_cnt += 1
        if (dir_a != self._dir_a) or (dir_b != self._dir_b):
            self._io.send_ser("MD{:d},{:d}".format(1 if dir_a else 0, 1 if dir_b else 0))
            self._dir_a = dir_a
            self._dir_b = dir_b
        if cmd != self._last_cmd:
            self._io.send_ser(cmd)
            self._last_cmd = cmd
        if self._mot_stop_cnt == self._mot_stop_cutoff:
            self._io.send_ser("MP0,0")
        if debug:
            print(cmd)
        
        
    def stop(self):
        self._io.send_ser("MR0,0")
        self._io.send_ser("MP0,0")
        
# main =================================================
if __name__ == "__main__":
    
    io = raspicar_ioctrl.IoCtrl()
    time.sleep(0.1)
    mot = Motors(io)
    
    print("Moving forward ...")
    mot.run(0, +30)
    time.sleep(2)
    mot.run(0, 0)
    time.sleep(1)
    
    print("Moving backward ...")
    mot.run(0, -30)
    time.sleep(2)
    mot.run(0, 0)
    time.sleep(1)
    
    print("Turning left ...")
    mot.run(-50, +30)
    time.sleep(2)
    mot.run(0, 0)
    time.sleep(1)

    print("Turning right ...")
    mot.run(+50, +30)
    time.sleep(2)
    mot.run(0, 0)
    time.sleep(1)

    mot.stop()
    io.close()
    

            