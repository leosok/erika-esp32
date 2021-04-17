
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
# scan_wlan()
# set time
try:
    ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
    ntptime.settime()
except:
    print("Could not set time.")

erika = Erika()


async def wlan_strength(max=5):
    while True:
        ip = do_connect()
        wlan = network.WLAN()
        strength = wlan.status('rssi')
        screen.network(ip,strength)
        await asyncio.sleep(max)

async def main():
    # Schedule three calls *concurrently*:
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue),
       start_mqqt_connection(erika),
       wlan_strength(1)
    )

from utils import umailgun
do_connect()
time.sleep(2)
umailgun.send_mailgun(umailgun.tsttxt)

asyncio.run(main())