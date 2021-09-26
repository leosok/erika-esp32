
print("main.py: Hello")

import time
from mqtt_connection import ErikaMqqt
import ntptime
from erika import Erika
import uasyncio as asyncio
import network

from utils.network_utils import do_connect, scan_wlan
import utils.screen_utils as screen
from config import UserConfig



def set_time():
    try:
        ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
        ntptime.settime()
    except:
        print("Could not set time.")

erika = Erika()

# Here we have to check, if a configuration is present.
# If not, we need ot gather data from the user.

erika_mqqt = ErikaMqqt(erika=erika)
erika.mqqt_client = erika_mqqt
user_config = UserConfig()

scan_wlan()

if user_config.load():
    do_connect(user_config.wlan_ssid, user_config.wlan_password)
    set_time()
else:
    asyncio.run(user_config.get_config_io(erika))
    user_config.load()



async def wlan_strength(user_config:UserConfig, max=5):
    while True:
        ip = do_connect(user_config.wlan_ssid, user_config.wlan_password)
        wlan = network.WLAN()
        strength = wlan.status('rssi')
       # screen.network(ip,strength)
        await asyncio.sleep(max)


#from config.first_config_io import start_first_config        
async def main():
    # Schedule three calls *concurrently*:
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue_print),
       erika_mqqt.start_mqqt_connection(),
       #wlan_strength(user_config),
       #start_first_config(erika)
    )

screen.starting()
asyncio.run(main())

