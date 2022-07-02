# boot.py
import time
import machine
machine.freq(240000000)

t_start = time.ticks_ms()
t_0 = t_start

print("boot.py, importing SpashScreen. Total {}ms ".format(t_start))
from utils.splash_screen import tft_splash_screen
print("SpashScreen imported in {}ms Running since: {}ms".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))
print("Splashing Screen")
tft_splash_screen()    
print("Spashscreen OK: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))


print("boot.py, importing screen. Total {}ms ".format(t_start))
from utils.screen_utils import Screen
print("Screen imported in {}ms Running since: {}ms".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))
print("I sleep")
t_0 = time.ticks_ms()
print(f"[start] loading Boardconfig:")
from config import BoardConfig
board_config = BoardConfig()
print("[done] loading Boardconfig: {}ms, total: {}ms".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))



try:
    t_0 = time.ticks_ms()
    print("import st7789")
    import st7789
    print("Import OK: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))

    t_0 = time.ticks_ms()
    print("creating screen object")
    from utils.screen_utils import Screen
    screen = Screen(board_type='TTGO_T_DISPLAY')
    print("Screen created OK: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))

  
    print("Splashing Screen")
    screen.splash_screen()
    print("Spashscreen OK: {}, total: {}".format(time.ticks_diff(time.ticks_ms(),t_0), time.ticks_ms()))
except:
    print("Not a TTGO_T_DISPLAY")


# print(f"[start] loading Boardconfig: {time.ticks_ms()}")
# from config import BoardConfig
# board_config = BoardConfig()
# print(f"[done] loading Boardconfig: {time.ticks_ms()}")

#import webrepl
#webrepl.start()
