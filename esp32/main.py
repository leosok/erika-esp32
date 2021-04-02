
print("main.py: Hello")

import time
from boot import do_connect
from screen_utils import inizilize_screen, screen_network
from mqtt_connection import start_mqqt_connection



ip = do_connect() 
oled = inizilize_screen()
screen_network(oled, ip)
#start_server(ip) #needs to be after screenstart because of UART
oled = inizilize_screen()
screen_network(oled)
start_mqqt_connection(check_msg_interval = 5000)