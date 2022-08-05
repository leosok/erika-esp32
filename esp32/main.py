print("main.py: Hello")
from utils import debug_log
deb = debug_log.Debuglogger("main")
from config.board_config import BoardConfig
board_config = BoardConfig()
from utils.screen_utils import Screen
screen = Screen(board_type=board_config.screen_display_type, display=display_obj.display)
# screen.show_image("mqqt4",200,10)
# screen.show_image("mqqt5",200,50)
# screen.show_image("mqqt3",200,80)

#sp_c = screen.play_sprite(x=200, y=15, name="cloud_sprites", width_height=30, frames=2, play_reverse=True, pause_sec=0.5)
# sp_w = screen.play_sprite(x=150) # 150 is the nice spot
# sp_w = screen.play_sprite(x=10)
from utils.sprite_utils import Sprite
wifi_status_sprite = Sprite(name="wlan_sprites", display=screen.display)
wifi_status_sprite.off()
mqqt_status_sprite = Sprite(name="cloud_sprites", display=screen.display, x=195, y=13, frames=2)


deb.start("imports")
from mqtt_connection import ErikaMqqt
import ntptime
from erika import Erika
import uasyncio as asyncio
import network
import machine
from utils import debug_log
from plugins import register_plugins
from utils.network_utils import do_connect, scan_wlan
deb.done()

# async def wlan_strength(user_config:UserConfig, max=5):
#     while True:
#         await asyncio.sleep(3)
#         ip = do_connect(user_config.wlan_ssid, user_config.wlan_password)
#         screen.network(ip)
#         await asyncio.sleep(max-1)

progress_timer.deinit() # is auto_loded from boot.py  
async def start_all(erika:Erika, mqqt:ErikaMqqt):
    # Schedule three calls *concurrently*:
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue_print),
       erika_mqqt.start_mqqt_connection(wifi_status_sprite, mqqt_status_sprite),
       #wlan_strength(user_config)    
       #sp_c,
       # sp_w)#, sp_c)
    )

async def start_config(erika:Erika):
    # Schedule three calls *concurrently*:
    from config import first_config_io
    erika.mqqt_send_keystrokes = False
    await asyncio.gather(
       erika.receiver(),
       erika.printer(erika.queue_print),
       first_config_io.FirstConfig().get_config_io(erika)
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

from config.user_config import UserConfig
user_config = UserConfig()

# Here we have to xcheck, if a configuration is present.
# If not, we need ot gather data from the user.


if user_config.load():
    #do_connect(user_config.wlan_ssid, user_config.wlan_password)
    #set_time()
    erika_mqqt = ErikaMqqt(erika=erika)
    erika.mqqt_client = erika_mqqt
    screen.splash_screen(reset=True)#write_to_screen("Erika",line=1,reset=True)
    
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
