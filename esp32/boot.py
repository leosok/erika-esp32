# boot.py
import machine
machine.freq(240000000)
from utils import debug_log
deb = debug_log.Debuglogger()
deb.start("import spashscreen")
from utils.splash_screen import Display
deb.done()
deb.start("tft_spash_screen()")
display=Display()
display.splash_screen()
deb.done()  
# deb.start("import Screen")
# from utils.screen_utils import Screen
# deb.done()
deb.start("load Boardconfig")
from config.board_config import BoardConfig
board_config = BoardConfig()
deb.done()

# try:
#     t_0 = time.ticks_ms()
#     print("import st7789")
#     import st7789
#     print("Import OK: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))

#     t_0 = time.ticks_ms()
#     print("creating screen object")
#     from utils.screen_utils import Screen
#     screen = Screen(board_type='TTGO_T_DISPLAY')
#     print("Screen created OK: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))

  
#     print("Splashing Screen")
#     screen.splash_screen()
#     print("Spashscreen OK: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))
# except:
#     print("Not a TTGO_T_DISPLAY")


# print(f"[start] loading Boardconfig: {time.ticks_ms()}")
# from config import BoardConfig
# board_config = BoardConfig()
# print(f"[done] loading Boardconfig: {time.ticks_ms()}")

#import webrepl
#webrepl.start()
