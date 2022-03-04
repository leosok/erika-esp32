
print("main.py: Hello")

# putting this up front to speed up
from utils.misc import status_led
import utils.screen_utils as screen
from config import UserConfig, BoardConfig

board_config = BoardConfig()

status_led(False)
print("starting screen...")
screen.starting(display_type=board_config.screen_display_type)
#screen.show_qr_code()


import time
from mqtt_connection import ErikaMqqt
import ntptime
from erika import Erika
import uasyncio as asyncio
import network
import machine

from utils.network_utils import do_connect, scan_wlan


async def wlan_strength(user_config:UserConfig, max=5):
    while True:
        ip = do_connect(user_config.wlan_ssid, user_config.wlan_password)
        screen.network(ip)
        await asyncio.sleep(max)
       
async def start_all(erika:Erika, mqqt:ErikaMqqt):
    # Schedule three calls *concurrently*:
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue_print),
       erika_mqqt.start_mqqt_connection(),
       wlan_strength(user_config)
    )

async def start_config(erika:Erika):
    # Schedule three calls *concurrently*:
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue_print),
       UserConfig().get_config_io(erika)
    )

def set_time():
    try:
        ntptime.NTP_DELTA = ntptime.NTP_DELTA - (2 * 3600) # Delta of -2 = UTC +2 = CEST
        ntptime.settime()
    except:
        print("Could not set time.")



###############################
#  ***      START       ***   #
###############################


erika = Erika(cts_pin=board_config.erika_cts, rts_pin=board_config.erika_rts)
user_config = UserConfig()


# Here we have to xcheck, if a configuration is present.
# If not, we need ot gather data from the user.

if user_config.load():
    do_connect(user_config.wlan_ssid, user_config.wlan_password)
    set_time()
    erika_mqqt = ErikaMqqt(erika=erika)
    erika.mqqt_client = erika_mqqt
    screen.write_to_screen("Erika",line=1,centered=True)
    asyncio.run(
        start_all(erika=erika, mqqt=erika_mqqt)
        )
else:
    print("No Config found. Asking User for it...")
    asyncio.run(
        start_config(erika=erika)
        )
    print("Restarting Erika...")
    machine.reset()
    #asyncio.run(main(erika=erika, mqqt=erika_mqqt))
