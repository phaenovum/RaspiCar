"""
Modul: raspicar_ioctrl.py
I/O interface for the RaspiCar
Runs battery voltage control and system shut down as background processes
This version 2 of IoCtrl is based on the RPi.GPIO library (and does not require PIGPIO)

- Class: IoCtrl
- Methods: send_msg, clear_display, set_led_green, set_led_red, set_lidar_pwr, close

SLW 01-12-2023
Last update: 01-12-2025
"""

from gpiozero import LED
# import RPi.GPIO
import time
import serial
import threading
import os

CHECK_VERSION = False

""" Battery status:
BAT_STATUS_EXTERN              0   // 'EX', external power supply
BAT_STATUS_OK                  1   // 'OK', battery voltage okay
BAT_STATUS_LOW                 2   // 'BL', battery voltage low, no immediate action required
BAT_STATUS_SHUTDOWN            3   // 'SX', shutdown is active, power will shut off shortly
BAT_STATUS_SHUTDOWN_REQUESTED  4   // 'SR', the user has pressed shutdown, waiting for confirmation
BAT_STATUS_SHUTDOWN_PENDING    5   // 'SP', shutdown was confirmed, waiting for acknowledgment by Raspi
"""

class IoCtrl:
       
    def __init__(self):
        # pin definitions
        _PIN_LED_RED = 6
        _PIN_LED_GREEN = 13
        _PIN_LIDAR_PWR = 21
        _serial_port = "/dev/ttyUSB0"
        _software_version = 0.0
        # initiate ports
        self._led_green = LED(_PIN_LED_GREEN)
        self._led_red = LED(_PIN_LED_RED)
        self._lidar_pwr = LED(_PIN_LIDAR_PWR)
        # initiate operating data
        self._ser_busy = False
        self.__shutdown = False
        self._status = "OK"
        # set initial values
        self._led_green.off()
        self._led_red.off()
        self._lidar_pwr.off()
        # initiate serial interface
        connection_cnt = 0
        connected = False
        while not connected and connection_cnt < 5:
            try:
                self._ser = serial.Serial(_serial_port, baudrate=115200,
                                      parity=serial.PARITY_NONE, timeout=1)
                connected = True
            except:
                msg = "warning: failed to open serial port" + str(connection_cnt)
                print(msg)
                time.sleep(2)
                connection_cnt += 1

        if self._ser.isOpen() == False:
            err_msg = "Error: can't open serial port " + _serial_port
            raise Exception(err_msg)            
        time.sleep(0.25)
        self.send_ser(" ");
        time.sleep(0.25)
        self.send_ser("DMRaspi connected")
        # check version
        if CHECK_VERSION:
            err_msg = ""
            msg = self.send_ser("GV")
            try:
                self._software_version = float(msg)
            except ValueError:
                err_msg = "Can't read interface software version! ('" + msg + ")'"
            if len(err_msg) > 0:
                raise Exception(err_msg)
            if self._software_version < 0.96:
                err_msg = "Interface software version " + str(self._software_version) + " not supported!"
                raise Exception(err_msg)
            print(" - ioctrl: interface software version:", self._software_version)
        # starting thread
        self._t = threading.Thread(target = self._read_status)
        self._t.start()       


    def _read_status(self):
        while not self.__shutdown:
            while self._ser_busy:
                time.sleep(0.01)
            self._status = self.send_ser("BS")[-2:]
            if self._status == "SP":
                print("Stopping motors ...")
                self.send_ser("MR0,0")
                time.sleep(0.1)
                self.send_ser("MP0,0")
                time.sleep(0.1)
                print("Shutting down")
                print(self.send_ser("BX"))
                time.sleep(0.1)
                os.popen("sudo shutdown -h now").read()
                
            time.sleep(1)
        print(" - ioctrl: status thread closed ...")


    def get_status(self) -> str:
        return self._status


    def set_lidar_pwr(self, pwr: bool):
        if pwr:
            self._lidar_pwr.on()
        else:
            self._lidar_pwr.off()


    def set_led_red(self, status: bool):
        if status:
            self._led_red.on()
        else:
            self._led_red.off()


    def set_led_green(self, status: bool):
        if status:
            self._led_green.on()
        else:
            self._led_green.off()


    def send_ser(self, msg: str, ser_delay=0.002) -> str:
        while self._ser_busy == True:
            time.sleep(ser_delay)
        self._ser_busy = True
        msg_bytes = bytes(msg + '\n', 'UTF-8')
        self._ser.write(msg_bytes)
        time.sleep(ser_delay)
        response = self._ser.readline()
        #response = bytes('OK', 'UTF-8')
        self._ser_busy = False
        return response[:-2].decode("UTF-8")
    
    
    def send_msg(self, msg: str):
        self.send_ser("DM" + msg)
        
    
    def send_titel(self, msg: str):
        self.send_ser("DT" + msg)
        
        
    def clear_display(self):
        self.send_ser("DC")
      
    
    def close(self):
        self.__shutdown = True
        time.sleep(1.5)
        self._ser.close()
        # self._shutdown = True
        
        
    @property
    def shutdown(self):
        return self.__shutdown
        
    

#------------------------------------------------
if __name__ == "__main__":
    io = IoCtrl()
    io.set_led_red(True)
    time.sleep(0.5)
    io.set_led_red(False)
    io.set_led_green(True)
    time.sleep(0.5)
    io.set_led_green(False)
    
    io.clear_display()
    io.send_titel("RaspiCar IoCtrl Test")
    io.send_msg("Hello!")
    
    io.set_lidar_pwr(True)
    time.sleep(2)
    io.set_lidar_pwr(False)
    time.sleep(1)

    io.close()
            
    
    