

from erika import char_map
import time
from machine import UART, Pin
from erika import erica_encoder_decoder

class Erika:
    DEFAULT_BAUD_RATE = 1200
    DEFAULT_LINE_LENGTH = 60
    DEFAULT_DELAY = 0.02
    RTS_PIN = 22
    CTS_PIN = 21
    SETTINGS_STRING = ";;:"


    def __init__(self):
      self.uart = self.start_uart()
      self.ddr_2_ascii = erica_encoder_decoder.DDR_ASCII()
      # It is important to PULL_DOWN the RTS_PIN, to get a reading! (0=OK, 1=busy, please wait)
      self.rts = Pin(Erika.RTS_PIN)
      self.rts.init(self.rts.IN, self.rts.PULL_DOWN)
      # Without setting CTS to low, Erika will not send data
      cts = Pin(Erika.CTS_PIN, Pin.OUT)
      cts.off

    ##########################

    def start_uart(self, rx=5, tx=17, baud=1200):
      uart=UART(2,baud)
      uart.init(baud,bits=8,parity=None,stop=1,rx=rx,tx=tx)
      print("uart started")
      return uart

    def read_string(self):
      tmp_str = ''
      while self.uart.any() > 0:
        tmp_bytes = self.uart.read(1)
        decoded_char = self.ddr_2_ascii.decode(tmp_bytes)
        tmp_str += decoded_char
      # print(tmp_str)  
      return tmp_str


    def print_string(self, text: str, linefeed=True):
      
      # output = ''
      # lines = self.string_to_lines(text)
      # print(lines)
      # for line in lines:
      for char in text:
        sent = False
        while not sent:      
            if self.rts.value() == 0:
                # Erika is ready
                char_encoded = self.ddr_2_ascii.encode(char)
                self.uart.write(char_encoded)
                sent = True
            else:
                sent = False
                time.sleep(Erika.DEFAULT_DELAY)
   

    # Returns an array of lines with a max_length of DEFAULT_LINE_LENGTH
    def string_to_lines(self, text, max_length=DEFAULT_LINE_LENGTH):
        #print("strtolines ({}): {}".format(max_length, text))
        words = text.split()
        lines = []
        tmp_line = ''

        # If the text is less than a line, return it
        if len(text) <= max_length:
          return [text]

        # else split to lines
        for word in words:
            next = ' '.join([tmp_line, word])
            if len(next) <= max_length:
                tmp_line = next
            else:
                lines.append(tmp_line.strip())
                tmp_line = word  
        
        # for the last words
        lines.append(tmp_line.strip())

        #print("strtolines ({}): {}".format(len(lines[0]), lines))
        return lines
        
