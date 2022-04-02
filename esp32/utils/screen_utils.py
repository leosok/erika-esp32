# screen_utils.py

from machine import SoftI2C, SoftSPI, Pin, sleep
import time
import gc



class BoardType:
    WIFI_KIT = 0
    D_DUINO = 1    
    TTGO_T_DISPLAY = 2 

class DisplayType:
    OLED = 0
    TFT = 1      


class Screen:
      
  def __init__(self, board_type = 'WIFI_KIT'):

    print("Display is " + board_type)    
    board_type = getattr(BoardType, board_type)

    
    self.display = None
    self.display_type = None
    self.board_type = board_type
    self.line_height = 10


    if board_type == BoardType.WIFI_KIT:
      import ssd1306
      rst = Pin(16, Pin.OUT)
      rst.value(1)
      scl = Pin(15, Pin.OUT, Pin.PULL_UP)
      sda = Pin(4, Pin.OUT, Pin.PULL_UP)
      i2c = SoftI2C(scl=scl, sda=sda, freq=450000)
      self.display_type = DisplayType.OLED
      self.display = ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3c)
    
    elif board_type == BoardType.D_DUINO:
      import sh1106
      sda = Pin(26)
      scl = Pin(27)
      i2c = SoftI2C(scl=scl, sda=sda, freq=400000)
      self.display_type = DisplayType.OLED
      self.display = sh1106.SH1106_I2C(128, 64, i2c, addr=0x3c)

    elif board_type == BoardType.TTGO_T_DISPLAY:
       
            
        self.display = self.get_tft()
        self.display_type = DisplayType.TFT

  def reset(self, lines=4, color=0):
        self.display.fill_rect(0, 0, self.display.width, self.line_height + lines*self.line_height, color)
        return True


  def get_tft(self):
      try:
        import st7789
      except ImportError as e: # type: ignore
        print("import error: " + e)
      spi = SoftSPI(baudrate=40000000, polarity=0,  sck=Pin(18), mosi=Pin(19), miso=Pin(2)) # Pin 2 is not really used
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
      return display  

  def get_random_color(self):
        import st7789, random
        return st7789.color565(
                random.getrandbits(8),
                random.getrandbits(8),
                random.getrandbits(8),
            )

  def splash_screen(self, text="starting...", reset=False):
    if self.display_type == DisplayType.TFT:
          #import vga1_8x8 as font 
      import meteo as font 
      from st7789 import WHITE
      print("splashscreen: " + text)

      # import scriptc as font
      if reset:
        tft=self.get_tft()
      else:
        tft=self.display
      tft.draw(font,"Erika",65,50, WHITE, 1.5)
      tft.draw(font,"electronic",65,85, WHITE, 0.8)

  def work_on_tft(self):
        from st7789 import BLUE
        self.splash_screen(reset=True)
        sleep(3)
        self.display.fill(BLUE)
        for i in range(1,5):
              self.write_to_screen(f"{i}: HALLO", line=i)



  def write_to_screen(self, text, margin=20, line=5, centered=False, font=None, reset=False):
    if self.display_type == DisplayType.OLED:
      oled = self.display
      # Screen is 16 char wide, each char 8 px
      print("Screen: " + text)
      oled.fill_rect(0, line*10, oled.width, 10, 0)
      if centered:
          empty_chars = 16-len(text)
          empty_width = round(empty_chars * 8 / 2)
          margin = empty_width 
      oled.text(text, margin, line*10)      
      oled.show()
    
    elif self.display_type == DisplayType.TFT:
      import romand as font 
      # import meteo as font 
      from st7789 import WHITE, BLACK
      BG_COLOR = BLACK
      scale = 0.65
      font_max_height = 32
      print("write_to_screen: " + text)

      # import scriptc as font
      if reset:
        tft=self.get_tft()
      else:
        tft=self.display

      # Display has 4 Lines now.
      import math
      padding = 5
      line_height =  math.ceil(font_max_height * scale) + padding
      print(f"line_height: {line_height}")
      line_y = padding + line_height * (line - 1)
      print(f"line: {line}; line_y: {line_y}")
      text_x = 5 # use this for centering!
      
      tft.fill_rect(0,line_y + (2*padding), tft.width(), line_height, BG_COLOR)
      tft.draw(font, text, text_x, line_y + line_height, self.get_random_color(),scale)
      gc.collect()

  def network(self, ip=False, strength=False):
    if ip:
      self.write_to_screen(ip,line=2)
    if strength:
      self.write_to_screen(str(strength),line=3)
    self.text(str(round(time.ticks_ms()/1000)))
    pass

  # def starting(self, display_type = "D_DUINO"):
  #   if self.display_type == DisplayType.OLED:
  #         oled = self.display
  #   display_type_enum = getattr(DisplayType, display_type)
  #   oled = inizilize(display_type=display_type_enum)
  #   oled = reset(5)
  #   write_to_screen('Erika loading...', line=1, centered=True)

  
  
  def show_progress(self, progress=0, max=100, line=5):
    if self.display_type == DisplayType.OLED:
      oled = self.display
        
      oled.fill_rect(0, line*10, oled.width, 10, 0)
      margin = 10
      current_width = round((oled.width-margin) / max * progress)
      oled.rect(margin, 50, oled.width-margin, 5, 50) # outer rect
      oled.fill_rect(margin, 50, current_width, 5, 50) # filling
      oled.rect(margin, 50, oled.width-margin, 5, 50) # outer rect
      oled.show()
    elif self.display_type == DisplayType.TFT:
      print("ToDo: Showprogress on TFT")


  # class Display:
        
  #   def __init__(self, display=None, display_type:DisplayType=None):
  #         self.display = display
  #         self.display_type=display_type
  #         if self.display_type == DisplayType.OLED:
  #           self.line_height = 10
  #         else:
  #           self.line_height = 10
                    

    


  # def show_qr_code(data="http://erika-cloud.de", size=1):
      # from uQR import QRCode
  #   oled = inizilize()
  #   oled = reset(5)
  #   print("making QRcode")
  #   qr = QRCode()
  #   qr.add_data(data)
  #   matrix = qr.get_matrix()
  #   for line_num, line_data in enumerate(matrix):
  #     for row_num, row_data in enumerate(line_data):
  #       oled.pixel(line_num, row_num, row_data)
  #   oled.show()
