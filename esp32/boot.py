# boot.py
import machine
machine.freq(240000000)
import time
print(time.ticks_ms())
from utils.splash_screen import Display
display_obj=Display()
display_obj.splash_screen()
print(time.ticks_ms())

display_obj.show_progress(progress=0, max=10, y_from=110, bar_height=10)

timer = machine.Timer(0)
interruptCounter = 0
def handleInterrupt(timer):
    global interruptCounter
    interruptCounter = interruptCounter+1
    global display_obj
    display_obj.show_progress(progress=interruptCounter, max=10, y_from=110, bar_height=10)
    #print(f"interruptCounter {interruptCounter} {time.ticks_ms()}")
    if interruptCounter >= 10:
        timer.deinit()

timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=handleInterrupt)