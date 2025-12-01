"""
RaspiCar Controller via socket UDP protocol
SLW - June-2023
"""

import time
import network
import socket
from machine import I2C, Pin, ADC, Timer
import os
from lcd_i2c import LCD

__version__ = '20230624'

#---------------------------------------------------------------------------    
def lcd_print(txt):
    lcd.set_cursor(col=0, row=0)
    lcd.print(lcd_rows[lcd_rows_pnt[1]])
    lcd.set_cursor(col=0, row=1)
    lcd.print(lcd_rows[lcd_rows_pnt[2]])
    lcd.set_cursor(col=0, row=2)
    lcd.print(lcd_rows[lcd_rows_pnt[3]])
    l = len(txt)
    if l > 20:
        lcd_rows[lcd_rows_pnt[0]] = txt[:20]
    else:
        lcd_rows[lcd_rows_pnt[0]] = txt + (20 - l) * ' '
    lcd.set_cursor(0, 3)
    lcd.print(lcd_rows[lcd_rows_pnt[0]])
    x = lcd_rows_pnt[0]
    lcd_rows_pnt[0] = lcd_rows_pnt[1]
    lcd_rows_pnt[1] = lcd_rows_pnt[2]
    lcd_rows_pnt[2] = lcd_rows_pnt[3]
    lcd_rows_pnt[3] = x
    
#---------------------------------------------------------------------------    
def read_config(config_file):
    # Read config file
    if config_file not in os.listdir():
        cfg = open(config_file, "w")
        cfg.write("RaspiCar Ctrl config file\n")
        cfg.write("port : 12000\n")
        cfg.write("lcd_timeout : 30\n")
        cfg.close()

    cfg = open(config_file)
    lines = cfg.readlines()
    cfg.close()

    config = {}
    for l in lines[1:]:
        l = l.replace('\n', ' ');
        key, value = l.split(':')
        config[key.strip(' ')] = value.strip(' ')
    return config


#---------------------------------------------------------------------------    
def write_config(config_file):
    # Write config file
    cfg = open(config_file, "w")
    cfg.write("RaspiCar Ctrl config file\n")
    for key, value in config.items():
        cfg.write(key + ' : ' + value + '\n')
    print("Config file saved!")
    cfg.close()


#---------------------------------------------------------------------------    
def try_connection(ssid, password, static_ip):
    """ Tries a connection on the given credentials.
    In case of success it returns True and ip address.
    In case of failure it returns False and 0.
    Requires an active wlan_node  """

    lcd_print("SSID: " + ssid)
    led_red.value(1)
    led_green.value(0)
    ssid_bytes = ssid.encode('UTF-8')  
    connected = False

    if static_ip != '<none>':
        last_dot = static_ip.rfind('.')
        gateway_ip = static_ip[:static_ip.rfind('.')] + '.1'
        lcd_print("Requesting static IP")
        wlan_node.ifconfig((static_ip, '255.255.255.0', gateway_ip, gateway_ip))

    for number_of_attempts in range(3):
        wlan_node.connect(ssid_bytes, password.encode('UTF-8'))
        for i in range(10):
            led_green.toggle()
            led_red.toggle()
            if wlan_node.isconnected():
                connected = True
                break
            time.sleep(0.5)    
        if connected:
            break
    
    if connected:
        led_red.value(0)
        led_green.value(1)
        time.sleep(0.5)
        server_ip_addr = wlan_node.ifconfig()[0]
        lcd_print("IP: " + server_ip_addr)
        return True, server_ip_addr
    else:
        lcd_print("failed ...")
        led_red.value(1)
        led_green.value(0)
        return False, '0'
    
#---------------------------------------------------------------------------
def connect_to_wlan(ssid_file):

    # Reading ssids from file
    try:
        with open(ssid_file, "r") as f:
            lines = f.readlines()
    except:
        print("Could not open " + ssid_file + "!")
        print("Closing")
        return None
    
    ssids = {}
    for l in lines:
        if len(l) > 2:
            data = l.split(',')
            if len(data) == 2:
                s, p = l.split(',')
                s, p, static_ip = s.strip(' '), p[:-2].strip(' '), '<none>'
                ssids[s] = (p, static_ip)
            elif len(data) == 3:
                s, p, static_ip = l.split(',')
                s, p, static_ip = s.strip(' '), p.strip(' '), static_ip[:-2].strip(' ')
                ssids[s] = (p, static_ip)
            else:
                print("SSID data error - can't decode line " + l)
                print("Program stopped")
                while True:
                    pass

    # Scanning network
    all_nets = [(net[0].decode('UTF-8'), net[3]) for net in wlan_node.scan()]
    # Limiting to know networks
    all_nets = [net for net in all_nets if net[0] in ssids.keys()]
    # Adding password and static IP
    all_nets = [(net[0], net[1], ssids[net[0]][0], ssids[net[0]][1]) for net in all_nets]
    
    # Finding suitable network and trying to connect
    server_ip_addr = '0.0.0.0'
    if len(all_nets) == 0:
        lcd_print("No network ...")
        while True:
            pass
    else:
        # Sort networks by signal strength
        all_nets = sorted(all_nets, key=lambda x: x[1], reverse=True)
        for net in all_nets:
            success, server_ip_addr = try_connection(net[0], net[2], net[3])
            if success:
                break

    return server_ip_addr


#---------------------------------------------------------------------------
def timer_interrupt(tim):
    """ Manage lcd backlight """
    global lcd_light_cnt, lcd_light_is_on

    if bt_blue.value() == 0:
        lcd_light_cnt = lcd_timeout

    if lcd_light_cnt == lcd_timeout:
        if not lcd_light_is_on:
            lcd.backlight()
            lcd_light_is_on = True
    elif lcd_light_cnt == 0:
        if lcd_light_is_on:
            lcd.no_backlight()
            lcd_light_is_on = False
    if lcd_light_cnt >= 0:
        lcd_light_cnt -= 1
    
        
#==============================================================================

# Pin definitions
led_green = Pin(20, Pin.OUT)
led_red = Pin(21, Pin.OUT)
bt_blue = Pin(6, Pin.IN, Pin.PULL_UP)
bt_green = Pin(7, Pin.IN, Pin.PULL_UP)
bt_yellow = Pin(8, Pin.IN, Pin.PULL_UP)
bt_red = Pin(9, Pin.IN, Pin.PULL_UP)
bt_joystick = Pin(10, Pin.IN, Pin.PULL_UP)

# Global constants
config_file_name = "raspicar_ctrl.config"
ssid_file_name = "ssid.dat"
config = read_config(config_file_name)

# Global variables
lcd_rows = [20 * ' ', 20 * ' ', 20 * ' ', 20 * ' ']
lcd_rows_pnt = [0, 1, 2, 3]
lcd_timeout = int(config['lcd_timeout']) * 4
lcd_light_cnt = lcd_timeout
lcd_light_is_on = True

# Initiate network
network.country('DE')
network.hostname(config.get('hostname', 'RaspiCarCrtl'))
wlan_node = network.WLAN(network.STA_IF)
wlan_node.active(True)

# Start LC display
i2c = I2C(0, sda=Pin(4), scl=Pin(5), freq=800000)
lcd = LCD(addr=0x27, cols=20, rows=4, i2c=i2c)
lcd.begin()
lcd_print("RaspiCar " + __version__)

# Toogle LEDs
led_green.value(1)
time.sleep(0.3)
led_green.value(0)
led_red.value(1)
time.sleep(0.3)
led_red.value(0)

# Connect to network
server_ip_addr = connect_to_wlan(ssid_file_name)
  
# Start socket server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((server_ip_addr, int(config['port'])))
lcd_print("Ready on port " +  config['port'])

# Initialze ADC
adcx = ADC(0)
adcy = ADC(1)

# Start periodic timer 
tim = Timer(mode=Timer.PERIODIC, period=250, callback=timer_interrupt)

# main loop 
try:
    while True:
        message, addr = server_socket.recvfrom(1024)
        if message[0] == ord('d'):   # read data
            buttons = ((bt_blue.value() == 0)     << 0)  |  \
                      ((bt_green.value() == 0)    << 1)  |  \
                      ((bt_yellow.value() == 0)   << 2)  |  \
                      ((bt_red.value() == 0)      << 3)  |  \
                      ((bt_joystick.value() == 0) << 4)
            response = str(buttons) + ',' + str(adcx.read_u16() // 64) + ',' + str(adcy.read_u16() // 64)
            server_socket.sendto(response, addr)
        elif message[0] == ord('t'):   # print message to display
            lcd_print(message[1:].decode('UTF-8'))
        elif message[0] == ord('x'):   # end program
            break
        lcd_light_cnt = lcd_timeout
        led_green.toggle()
except KeyboardInterrupt:
    pass

lcd_print("Closing program ...")
server_socket.close()
wlan_node.disconnect()
wlan_node.active(False)
del(tim)
lcd.backlight()
led_green.value(0)
led_red.value(0)
lcd_print("Good bye!")
