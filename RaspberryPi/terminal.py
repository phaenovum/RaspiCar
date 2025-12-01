"""
terminal.py

A simple terminal script to pay with the serial interface fpr the RaspiCar motor controller

SLW 11/2025
"""

import serial
import time

def send_ser(msg, ser_delay=0.05):
    msg_bytes = bytes(msg + '\n', 'UTF-8')
    ser.write(msg_bytes)
    time.sleep(ser_delay)
    response = ser.readline()
    return response[:-2].decode("UTF-8")

# main program starts here ==================================

connection_cnt = 0
connected = False
serial_port = "/dev/ttyUSB0"
while not connected and connection_cnt < 5:
    try:
        ser = serial.Serial(serial_port, baudrate=115200,
                            parity=serial.PARITY_NONE, timeout=1)
        connected = True
    except (FileNotFoundError, serial.serialutil.SerialException) as e: 
        print(e)
        time.sleep(2)
        connection_cnt += 1
        print("Trying again:", connection_cnt)
        
if not connected:
    raise Exception("Error! Can't open serial port " + serial_port)

time.sleep(0.2)
print("Connection:", send_ser('x'))
print("Quit with 'quit'<return>")
time.sleep(1)
    
while True:
    msg = input("> ")
    if msg[:4].casefold() in ("quit", "exit"):
        break
    response = send_ser(msg)
    print(response)
        
send_ser("MR0,0")
send_ser("MP0,0")
send_ser("ME0,0")
ser.close()
print("Serial interface closed ...")
    