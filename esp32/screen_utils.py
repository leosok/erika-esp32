# screen_utils.py

from boot import do_connect
from machine import SoftI2C, Pin
import ssd1306
print("Show Wlan on Screen now")

def inizilize_screen():
  rst = Pin(16, Pin.OUT)
  rst.value(1)
  scl = Pin(15, Pin.OUT, Pin.PULL_UP)
  sda = Pin(4, Pin.OUT, Pin.PULL_UP)
  i2c = SoftI2C(scl=scl, sda=sda, freq=450000)
  oled = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
  return oled

def screen_network(oled, ip=False):
  oled.fill(0)
  oled.text('Erika', 45, 5)
  #oled.text('MicroPython', 20, 20)
  if ip:
    oled.text(ip,0,20)
  else:
    oled.text(do_connect(),0,20)
  oled.show()


def write_to_screen(text):
  print("txt: " + text)
  oled = inizilize_screen()
  # reset
  oled.fill_rect(0, 50, oled.width, oled.height-50, 0)
  oled.text(text, 20, 50)
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

