from machine import Pin, SoftSPI
import time
try:
    import st7789
    import meteo as font 
    from st7789 import WHITE

except ImportError as e: # type: ignore
    print("import error: " + e)

def tft_splash_screen():
  """fast loading for just the start-screen"""
  spi = SoftSPI(baudrate=20000000, polarity=0,  sck=Pin(18), mosi=Pin(19), miso=Pin(2)) # Pin 2 is not really used
  w=240
  h=135
  display = st7789.ST7789(
      spi, h, w,
      cs = Pin(5, Pin.OUT),
      backlight = Pin(4, Pin.OUT),
      reset=Pin(23, Pin.OUT),
      dc=Pin(16, Pin.OUT),
      rotation=1
  )
  display.init()
  # import scriptc as font
  display.draw(font,"Erika",65,50, WHITE, 1.5)
  display.draw(font,"electronic",65,85, WHITE, 0.8)
