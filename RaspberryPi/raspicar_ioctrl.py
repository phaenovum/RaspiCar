"""
Modul: raspicar_ioctrl.py
I/O interface for the RaspiCar
Runs battery voltage control and system shut down as background processes
This version 2 of IoCtrl is based on the RPi.GPIO library (and does not require PIGPIO)

- Class: IoCtrl
- Methods: send_msg, clear_display, set_led_green, set_led_red, set_lidar_pwr, close

SLW 02-12-2023
Last update: 01-12-2025
"""

import RPi.GPIO as GPIO
import time
import serial
import threading
import os

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
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        # pin definitions
        _PIN_LED_RED = 13
        _PIN_LED_GREEN = 6
        _PIN_LIDAR_PWR = 21
        _serial_port = "/dev/ttyUSB0"
        # initiate ports
        self.pin_led_green, self.pin_led_red = _PIN_LED_GREEN, _PIN_LED_RED
        self.pin_lidar_pwr = _PIN_LIDAR_PWR
        # initiate operating data
        self._ser_busy = False
        self.__shutdown = False
        self._status = "OK"
        # set port mode
        GPIO.setup(self.pin_led_green, GPIO.OUT)
        GPIO.setup(self.pin_led_red, GPIO.OUT)
        GPIO.setup(self.pin_lidar_pwr, GPIO.OUT)
        # set initial values
        GPIO.output(self.pin_lidar_pwr, 0)
        GPIO.output(self.pin_led_green, 0)
        GPIO.output(self.pin_led_red, 0)
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
        time.sleep(0.5)
        self.send_ser(" ");
        time.sleep(0.5)
        self.send_ser("DMRaspi connected")
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
        print(" - io_ctrl: status thread closed ...")


    def get_status(self):
        return self._status


    def set_lidar_pwr(self, pwr):
        if pwr:
            GPIO.output(self.pin_lidar_pwr, 1)
        else:
            GPIO.output(self.pin_lidar_pwr, 0)


    def set_led_red(self, status):
        if status:
            GPIO.output(self.pin_led_red, 1)
        else:
            GPIO.output(self.pin_led_red, 0)


    def set_led_green(self, status):
        if status:
            GPIO.output(self.pin_led_green, 1)
        else:
            GPIO.output(self.pin_led_green, 0)


    def send_ser(self, msg, ser_delay=0.002):
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
    
    
    def send_msg(self, msg):
        self.send_ser("DL" + msg)
        
        
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
    io.send_msg("Hello!")
    
    io.set_lidar_pwr(True)
    time.sleep(2)
    io.set_lidar_pwr(False)
    time.sleep(1)

    io.close()
            
    
    