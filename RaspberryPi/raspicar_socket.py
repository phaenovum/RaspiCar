"""
Modul: raspicar_socket.py
UDP socket connection for the RaspiCar

- Class: RaspiCarSocket
- Methods: send_msg, get_data, get_stats, close

SLW 16-06-2023
"""

import time
import socket
import subprocess
import os


class RaspiCarSocket:
    
    def __init__(self):
        self._port_no = 12000
        self._latency = []
        self._timeout_cnt = 0
        self._max_timeout_cnt = 10
        self._timeout_sum = 0
        # Joystick calibration data
        self._x_midpoint = 455
        self._xmin, self._xmax = 20, 980
        self._x_mute = 15
        self._y_midpoint = 457
        self._ymin, self._ymax = 80, 950
        self._y_mute = 15
        # Read expected IP addresses
        if self._read_ip_addr():
            self._ssid = self._get_ssid()
            self._server_ip_addr = self._expected_server_ip_addr[self._ssid]
            self._raspi_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._raspi_socket.settimeout(0.5)
            self._okay = True
        else:
            self._okay = False
            
        
    def _get_ssid(self):
        ssid = subprocess.check_output(['sudo', 'iwgetid']).decode().split(':')[1]
        ssid = ssid.strip('\n')
        ssid = ssid.strip('"')
        return ssid
        
        
    def _read_ip_addr(self):
        """ read expected server IP addresses """
        try:
            with open("ip_addr.dat", "r") as f:
                lines = f.readlines()
        except IOError:
            print(" - socket error: could not open file 'ip_addr.dat'")
            return False
        if len(lines) == 0:
            print(" - socket error: no ip addresses found")
            return False
        self._expected_server_ip_addr = {}
        for l in lines:
            if len(l) > 4:
                ssid, ip_addr = l[:-1].split(':')
                self._expected_server_ip_addr[ssid.strip(' ')] = ip_addr.strip(' ')
        return True
    
    
    def send_msg(self, msg):
        message = 't' + msg
        self._raspi_socket.sendto(message.encode('UTF-8'), (self._server_ip_addr, self._port_no))
        
        
    def get_data(self):
        success = True
        start_time = time.time()
        self._raspi_socket.sendto(b'd', (self._server_ip_addr, self._port_no))
        try:
            data, _ = self._raspi_socket.recvfrom(32)
            self._latency.append(time.time() - start_time)
            buttons, adcx, adcy = [int(z) for z in data.decode('UTF-8').split(',')]
            if adcx < self._x_midpoint - self._x_mute:
                x = -round((adcx - self._x_midpoint - self._x_mute) * 100 / (self._x_midpoint - self._xmin + self._x_mute))
            elif adcx > self._x_midpoint + self._x_mute:
                x = -round((adcx - self._x_midpoint + self._x_mute) * 100 / (self._xmax - self._x_midpoint + self._x_mute))
            else:
                x = 0
            if adcy < self._y_midpoint - self._y_mute:
                y = round((adcy - self._y_midpoint - self._y_mute) * 100 / (self._y_midpoint - self._ymin + self._y_mute))
            elif adcy > self._y_midpoint + self._y_mute:
                y = round((adcy - self._y_midpoint + self._y_mute) * 100 / (self._ymax - self._y_midpoint + self._y_mute))
            else:
                y = 0
            self._timeout_cnt = 0
        except socket.timeout:
            success = False
            buttons, x, y = 0, 0, 0
            self._timeout_sum += 1
            self._timeout_cnt += 1
            if self._timeout_cnt > self._max_timeout_cnt:
                print(" - socket error: socket connection failed!")
                self._okay = False
                return False, 0, 0, 0
        return success, buttons, x, y
        
        
    def get_stats(self):
        cnt = len(self._latency)
        if cnt > 0:
            return cnt, self._timeout_sum, \
                   round(min(self._latency) * 1000, 1), round(sum(self._latency) * 1000 / cnt, 1), round(max(self._latency) * 1000, 1)
        else:
            return 0, cnt, self._timeout_cnt, 0.0, 0.0, 0.0
    
    
    def get_latencies(self):
        return self._latency
    
   
    def close(self):
        print(" - socket: closing ...")
        self._raspi_socket.close()
                   
        
    @property
    def ssid(self):
        return self._ssid
    
    @property
    def server_ip_addr(self):
        return self._server_ip_addr
    
    @property
    def okay(self):
        return self._okay
    
        
#-------------------------------------------------------------
        
if __name__ == '__main__':
    
    s = RaspiCarSocket()
    
    print("SSID:", s.ssid)
    print("IP:", s.server_ip_addr)
    print("Okay:", s.okay)
    
    if not s.okay:
        print("Socket initiation failed!")
    else:
        print("SSID:", s.ssid)
        print("Server ip addr:", s.server_ip_addr)
        s.send_msg("Hello from Raspi")
        time.sleep(0.5)
        for i in range(100):
            success, buttons, x, y = s.get_data()
            if not s.okay:
                break
            if success:
                print(buttons, x, y)
            
            time.sleep(0.1)

    if not s.okay:
        print("Script stopped with errors!")
    else:
        print()
        print("Statistics:")
        stats = s.get_stats()
        print(" - returned:", str(stats[0]), "   Missed:", str(stats[1]))
        print(" - round trip (msec): min", str(stats[2]), " mean:", str(stats[3]), " max:", str(stats[4]))
        print()
        
        fig, ax = plt.subplots()
        ax.hist([l * 1000 for l in s.get_latencies()])
        ax.set_ylabel("Latency")
        ax.set_xlabel("msec")
        plt.show()
        
        s.send_msg("Okay, done!")
    
    s.close()
        
