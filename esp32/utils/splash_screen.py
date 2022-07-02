from machine import Pin, SoftSPI
import time
try:
    import st7789
    import meteo as font 
    from st7789 import WHITE

except ImportError as e: # type: ignore
    print("import error: " + e)


class Display:
    """
    Everything here is prefilled for TTGO-T-Display. Modularity is possible with BoardConfig,
    but loading time is more important right now.
    """
    def __init__(self):
        spi = SoftSPI(baudrate=20000000, polarity=0,  sck=Pin(18), mosi=Pin(19), miso=Pin(2)) # Pin 2 is not really used
        w=240
        h=135
        self.display = st7789.ST7789(
            spi, h, w,
            cs = Pin(5, Pin.OUT),
            backlight = Pin(4, Pin.OUT),
            reset=Pin(23, Pin.OUT),
            dc=Pin(16, Pin.OUT),
            rotation=1
        )
        self.display.init()
        
    def splash_screen(self):
        """fast loading for just the start-screen"""
        # import scriptc as font
        self.display.draw(font,"Erika",65,50, WHITE, 1.5)
        self.display.draw(font,"electronic",65,85, WHITE, 0.8)
