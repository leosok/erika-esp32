
print("main.py: Hello")

import time
from boot import do_connect
from screen_utils import inizilize_screen, screen_network
#from mqtt_connection import start_mqqt_connection
import ntptime
from erika import Erika



ip = do_connect() 
# set time
try:
    ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
    ntptime.settime()
except:
    print("Could not set time.")
oled = inizilize_screen()
screen_network(oled, ip)
#start_mqqt_connection(check_msg_interval = 5000)

erika = Erika()
oled = inizilize_screen()
screen_network(oled)
erika.start_receiver()

