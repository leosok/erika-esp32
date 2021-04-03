
print("main.py: Hello")

import time
from boot import do_connect
from screen_utils import inizilize_screen, screen_network
from mqtt_connection import start_mqqt_connection
import ntptime


ip = do_connect() 
# set time
ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
ntptime.settime()
oled = inizilize_screen()
screen_network(oled, ip)
#start_server(ip) #needs to be after screenstart because of UART
oled = inizilize_screen()
screen_network(oled)
start_mqqt_connection(check_msg_interval = 5000)