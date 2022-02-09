# screen_utils.py

from machine import SoftI2C, Pin 
import time
from uQR import QRCode

class DisplayType:
    WIFI_KIT = 0
    D_DUINO = 1           

oled = False

def inizilize(display_type = DisplayType.D_DUINO):
  global oled

  if display_type == DisplayType.WIFI_KIT:
    import ssd1306
    print("Display is Wifi_Kit ")
    scl = Pin(15, Pin.OUT, Pin.PULL_UP)
    sda = Pin(4, Pin.OUT, Pin.PULL_UP)
    i2c = SoftI2C(scl=scl, sda=sda, freq=450000)
    oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
  
  elif display_type == DisplayType.D_DUINO:
    import sh1106
    print("Display is D-Duino ")
    sda = Pin(26)
    scl = Pin(27)
    i2c = SoftI2C(scl=scl, sda=sda, freq=400000)
    oled = sh1106.SH1106_I2C(128, 64, i2c, addr=0x3c)
        
  return oled

def reset(lines=4):
  oled.fill_rect(0, 0, oled.width, 10 + lines*10, 0)
  # oled.show()
  return oled

def network(ip=False, strength=False):
  reset()
  oled.text('Erika', 45, 5)
  if ip:
    oled.text(ip,0,20)
  if strength:
    oled.text(str(strength), 0, 30)
  oled.text(str(round(time.ticks_ms()/1000)), 0, 40)
  oled.show()

def starting():
  oled = inizilize()
  oled = reset(5)
  write_to_screen('Erika loading..', line=1, centered=True)
  write_to_screen('zweite', line=2, centered=True)

def write_to_screen(text, margin=20, line=5, centered=False):
  # Screen is 16 char wide, each char 8 px
  print("Screen: " + text)
  oled.fill_rect(0, line*10, oled.width, 10, 0)
  if centered:
      empty_chars = 16-len(text)
      empty_width = round(empty_chars * 8 / 2)
      margin = empty_width 
  oled.text(text, margin, line*10)
  
  oled.show()
 
def show_progress(progress=0, max=100, line=5):
  oled.fill_rect(0, line*10, oled.width, 10, 0)
  margin = 10
  current_width = round((oled.width-margin) / max * progress)
  oled.rect(margin, 50, oled.width-margin, 5, 50) # outer rect
  oled.fill_rect(margin, 50, current_width, 5, 50) # filling
  oled.rect(margin, 50, oled.width-margin, 5, 50) # outer rect
  oled.show()


def show_qr_code(data="http://erika-cloud.de", size=1):
  oled = inizilize()
  oled = reset(5)
  print("making QRcode")
  qr = QRCode()
  qr.add_data(data)
  matrix = qr.get_matrix()
  for line_num, line_data in enumerate(matrix):
    for row_num, row_data in enumerate(line_data):
      oled.pixel(line_num, row_num, row_data)
  oled.show()


def sleep_player():
  import time
  n=1
  while True:
    if n <= 1:
      i = 1
      color = 1
    if n >= oled.width:
      i = -1
      color = 0
    n += i
    # reset
    oled.fill_rect(0, 0, oled.width, oled.height, 0)
    # new
    oled.fill_rect(0,0,n,oled.height, 1)
    oled.text("Schafe: "+str(n),n-90,10,0)
    oled.text("Leo in Bett",n-90,20,0)
    oled.show()
    time.sleep(0.01)

