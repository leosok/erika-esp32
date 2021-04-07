
print("main.py: Hello")

import time
from boot import do_connect
import utils.screen_utils as screen
from mqtt_connection import start_mqqt_connection, check_channel
import ntptime
from erika import Erika
import uasyncio as asyncio


screen.starting()
ip = do_connect() 
# set time
try:
    ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
    ntptime.settime()
except:
    print("Could not set time.")
screen.network(ip)

erika = Erika()
screen.network(ip)


# Start all that Jazz
loop = asyncio.get_event_loop()
loop.create_task(erika.receiver())
print("Erika now listening to Keyboard async")
loop.create_task(erika.printer(erika.queue))
print("Erika now listening Print-Queue async")
# start_mqqt_connection(erika)
# print("MQQT now listening to server")
# loop.create_task(check_channel())
loop.run_forever()