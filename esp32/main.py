
print("main.py: Hello")

# putting this up front to speed up
from utils.misc import status_led
import utils.screen_utils as screen
from config import UserConfig, BoardConfig
import gc

board_config = BoardConfig()

status_led(False)
print("starting screen...")
screen = screen.Screen(board_type=board_config.screen_display_type)
screen.splash_screen("starting...")

# screen.starting(display_type=board_config.screen_display_type)
gc.collect()
print(gc.mem_free())
import ubinascii, machine, time
uuid = ubinascii.hexlify(machine.unique_id()).decode()
screen.show_qr_code(data = "http://www.erika-cloud.de/keycast/{}".format(uuid), scale=3)
gc.collect()
time.sleep(3)
print(gc.mem_free())

import time
from mqtt_connection import ErikaMqqt
import ntptime
from erika import Erika
import uasyncio as asyncio
import network
import machine
from plugins import register_plugins

from utils.network_utils import do_connect, scan_wlan


async def wlan_strength(user_config:UserConfig, max=5):
    while True:
        await asyncio.sleep(3)
        ip = do_connect(user_config.wlan_ssid, user_config.wlan_password)
        screen.network(ip)
        await asyncio.sleep(max-1)
       
async def start_all(erika:Erika, mqqt:ErikaMqqt):
    # Schedule three calls *concurrently*:
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue_print),
       erika_mqqt.start_mqqt_connection(),
       wlan_strength(user_config)    )

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

erika = Erika(cts_pin=board_config.erika_cts, 
        rts_pin=board_config.erika_rts, 
        tx_pin=board_config.erika_tx,  
        rx_pin=board_config.erika_rx,  
        screen=screen)
        
user_config = UserConfig()


# Here we have to xcheck, if a configuration is present.
# If not, we need ot gather data from the user.


if user_config.load():
    #do_connect(user_config.wlan_ssid, user_config.wlan_password)
    #set_time()
    erika_mqqt = ErikaMqqt(erika=erika)
    erika.mqqt_client = erika_mqqt
    screen.write_to_screen("Erika",line=1,reset=True)
    
    register_plugins(erika=erika, erika_mqqt=erika_mqqt)

    asyncio.run(
        start_all(erika=erika, mqqt=erika_mqqt)
        )
    
    # erika.screen.work_on_tft()
else:
    print("No Config found. Asking User for it...")
    asyncio.run(
        start_config(erika=erika)
        )
    print("Restarting Erika...")
    machine.reset()
    #asyncio.run(main(erika=erika, mqqt=erika_mqqt))
