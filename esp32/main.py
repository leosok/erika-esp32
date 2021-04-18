
print("main.py: Hello")

import time
from boot import do_connect, scan_wlan
import utils.screen_utils as screen
from mqtt_connection import ErikaMqqt
import ntptime
from erika import Erika
import uasyncio as asyncio
import network


def set_time():
    try:
        ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
        ntptime.settime()
    except:
        print("Could not set time.")

erika = Erika()
erika_mqqt = ErikaMqqt(erika=erika)


async def wlan_strength(max=5):
    while True:
        ip = do_connect()
        wlan = network.WLAN()
        strength = wlan.status('rssi')
        screen.network(ip,strength)
        await asyncio.sleep(max)

async def wlan_keep_alive(sleep=5):
    while True:
        do_connect()
        await asyncio.sleep(sleep)

        
async def main():
    # Schedule three calls *concurrently*:
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue),
       erika_mqqt.start_mqqt_connection(),
       wlan_strength(1)
    )

screen.starting()
do_connect()
set_time()
asyncio.run(main())