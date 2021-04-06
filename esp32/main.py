
print("main.py: Hello")

import time
from boot import do_connect
import utils.screen_utils as screen
#from mqtt_connection import start_mqqt_connection
import ntptime
from erika import Erika


screen.starting()
ip = do_connect() 
# set time
try:
    ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
    ntptime.settime()
except:
    print("Could not set time.")
screen.network(ip)
#start_mqqt_connection(check_msg_interval = 5000)

erika = Erika()
screen.network(ip)
erika.start_receiver()