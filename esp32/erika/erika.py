

from erika import char_map
from time import sleep
from machine import UART

class Erika:
    DEFAULT_BAUD_RATE = 1200
    DEFAULT_LINE_LENGTH = 60

    def __init__(self):
      self.connection = self.start_uart()

    ##########################

    def start_uart(self, rx=5, tx=17, baud=1200):
      uart=UART(2,baud)
      uart.init(baud,bits=8,parity=None,stop=1,rx=rx,tx=tx)
      print("uart started")
      return uart

    def read_string(self, size: int = 1):
        return self._read_bytes(size=size).decode("DDRSCII")

    def print_string(self, text: str):
      
      output = ''
      lines = self.string_to_lines(text)
      print(lines)
      for line in lines:
        for char in line:
          try:
            output = char_map.A2E[char]
          except:
            output = char_map.A2E['_']
          finally:
            self.connection.write(output)
            sleep(0.2)
        # End of line
        eol = char_map.A2E["\n"]
        self.connection.write(eol)
        sleep_carrige_time = (len(line)*0.04)
        print("carrige return. waiting {}".format(sleep_carrige_time))
        sleep(sleep_carrige_time) # check if this is good for carrige return
      
    

    # Returns an array of lines with a max_length of DEFAULT_LINE_LENGTH
    def string_to_lines(self, text, max_length=DEFAULT_LINE_LENGTH):
        print("strtolines ({}): {}".format(max_length, text))
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

        print("strtolines ({}): {}".format(len(lines[0]), lines))
        return lines
        
