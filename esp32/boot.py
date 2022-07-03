# boot.py
import machine
machine.freq(240000000)
from utils import debug_log
deb = debug_log.Debuglogger()
deb.start("import spashscreen")
from utils.splash_screen import Display
deb.done()
deb.start("tft_spash_screen()")
display_obj=Display()
display_obj.splash_screen()
deb.done()  

#import webrepl
#webrepl.start()
