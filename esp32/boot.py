# boot.py
import machine
import time
print(time.ticks_ms())
#from utils.splash_screen import Display
# import splash_screen
# display_obj=splash_screen.Display()
# display_obj.splash_screen()
# already done in frozen modules
print(time.ticks_ms())

# Loading Screen
progress_timer = machine.Timer(0)
interruptCounter = 0

def draw_loading_progress(timer):
    global interruptCounter
    global display_obj
    display_obj.show_progress(progress=interruptCounter, max=7, y_from=110, bar_height=10)
    interruptCounter = interruptCounter+1
    # if interruptCounter >= 11:
    #     timer.deinit()

progress_timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=draw_loading_progress)