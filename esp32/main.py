
print("main.py: Hello")

import time
from boot import do_connect, scan_wlan
import utils.screen_utils as screen
from mqtt_connection import start_mqqt_connection
import ntptime
from erika import Erika
import uasyncio as asyncio
import network


screen.starting()
scan_wlan()
ip = do_connect() 
# set time
try:
    ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
    ntptime.settime()
except:
    print("Could not set time.")
screen.network(ip)

erika = Erika()


async def wlan_strength(max=5):
    while True:
        wlan = network.WLAN()
        strength = wlan.status('rssi')
        screen.network(do_connect(),strength)
        await asyncio.sleep(max)

async def main():
    # Schedule three calls *concurrently*:
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue),
       start_mqqt_connection(erika),
       wlan_strength(1)
    )

asyncio.run(main())