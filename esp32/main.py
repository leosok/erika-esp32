
import time
print("main.py: Hello")
t_0 = time.ticks_ms()
print(f"[start] main imports: {time.ticks_ms()}")
import time
from mqtt_connection import ErikaMqqt
import ntptime
from erika import Erika
import uasyncio as asyncio
import network
import machine
print("[done] main imports: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))
print("[start] plugin imports")
t_0 = time.ticks_ms()
from plugins import register_plugins
print("[done] plugin imports: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))



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
    from config import first_config_io
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue_print),
       first_config_io.get_config_io(erika)
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
t_0 = time.ticks_ms()
print(f"[start] loading Boardconfig:")
from config import BoardConfig
board_config = BoardConfig()
print("[done] loading Boardconfig: {}ms, total: {}ms".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))

erika = Erika(cts_pin=board_config.erika_cts, 
        rts_pin=board_config.erika_rts, 
        tx_pin=board_config.erika_tx,  
        rx_pin=board_config.erika_rx,  
        screen=screen)   

print(f"[start] loading UserConfig: {time.ticks_ms()}")
from config import UserConfig
user_config = UserConfig()
print(f"[done] loading UserConfig: {time.ticks_ms()}")





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
