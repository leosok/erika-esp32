

from erika import char_map
import time
from machine import UART, Pin
from erika import erica_encoder_decoder
import binascii
import uasyncio as asyncio
from screen_utils import write_to_screen
from utils.pastebin import Pastebin 


# async def sender():
#     swriter = asyncio.StreamWriter(uart, {})
#     while True:
#         await swriter.awrite('Hello uart\n')
#         await asyncio.sleep(2)
#         print('wrote')



class Erika:
    DEFAULT_BAUD_RATE = 1200
    DEFAULT_LINE_LENGTH = 60
    DEFAULT_DELAY = 0.02
    RTS_PIN = 22
    CTS_PIN = 21
    SETTINGS_STRING = ";;:"

    def __init__(self):
        # line_buffer will be filled until "Return" is hit
        self.input_line_buffer = ''
        # lines_buffer will save the whole texte before doing sth with it.
        self.input_lines_buffer = []

        self.uart = self.start_uart()
        self.ddr_2_ascii = erica_encoder_decoder.DDR_ASCII()
        # It is important to PULL_DOWN the RTS_PIN, to get a reading! (0=OK, 1=busy, please wait)
        self.rts = Pin(Erika.RTS_PIN)
        self.rts.init(self.rts.IN, self.rts.PULL_DOWN)
        # Without setting CTS to low, Erika will not send data
        cts = Pin(Erika.CTS_PIN, Pin.OUT)
        cts.off

        self.sender = self.Sender(self)
        self.settings_controller = self.SettingsController(self)
        # asyncio
        # self.start_receiver()


    def start_receiver(self):
        loop = asyncio.get_event_loop()
        #loop.create_task(sender())
        loop.create_task(self.receiver())
        print("Erika now listening async")
        loop.run_forever()
    
    async def receiver(self):
        sreader = asyncio.StreamReader(self.uart)
        while True:
            tmp_bytes = await sreader.read(1)
            decoded_char = self.ddr_2_ascii.decode(tmp_bytes)        
            if decoded_char=='\n':
                current_line = self.input_line_buffer
                self.input_lines_buffer.append(current_line)
                if self.settings_controller.check_for_settings(current_line) == False:
                    self._save_lines_to_file(current_line)
                self.input_line_buffer = ''
            elif decoded_char == 'DEL':
                # remove last character, if DEL was hit
                self.input_line_buffer = self.input_line_buffer[:-1]
            elif decoded_char == self.SETTINGS_STRING[-1:]:
                self.input_line_buffer += decoded_char
                # If we hit the last Char of SETTINGSSTRING check if the rest was typed
                last_chars = self.input_line_buffer[-len(self.SETTINGS_STRING):]
                if last_chars == self.SETTINGS_STRING:
                    self.sender.alarm()
                    write_to_screen("Settings")
            else:
                self.input_line_buffer += decoded_char
            

    ##########################

    def start_uart(self, rx=5, tx=17, baud=1200):
        uart = UART(2, baud)
        uart.init(baud, bits=8, parity=None, stop=1, rx=rx, tx=tx)
        print("uart started")
        return uart

    def reader(self):
        pass

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

    def _save_lines_to_file(self, lines, filename='saved_lines.txt'):
        f = open(filename, 'a')
        # if it's just one line fake an array
        if type(lines) is str:
            lines = [lines]
        # save to file
        for line in lines:
            f.write(line + '\n')
        f.close()





    class SettingsController:

        def __init__(self, erika=None):
            self.erika = erika
            self.setting_string = erika.SETTINGS_STRING
        
        actions = {
            "hallo": "Print Hallo Welt",
            "save": "Save Buffer to Pastebin",
            "help": "Prints this info",
            "typing": "Turn echo ON/OFF",
            "save": "Saving full buffer to PasteBin"
        }
        
        def check_for_settings(self, input:str):
            if self.setting_string in input:
                c_string_start = input.rfind(self.setting_string) + len(self.setting_string)
                control_string = input[-len(input) + c_string_start:] # the last characters after SETTINGS_STRING          
                self.action(control_string)
            else:
                return False

        def action(self, action_str:str):
            action_str = action_str.replace(' ','_')
            print(action_str)
            try:
                if '_on' in action_str.lower():
                    method_name = action_str[:-len('_on')]
                    method_to_call = getattr(self,method_name)
                    method_to_call(True)
                elif '_off' in action_str.lower():
                    method_name = action_str[:-len('_off')]
                    method_to_call = getattr(self, method_name)
                    method_to_call(False)
                else:
                    method_to_call = getattr(self, action_str)
                    method_to_call()
            except AttributeError:
                print("Could not execute '{}'".format(action_str))

        def hallo(self):
            '''Prints a "hello"'''
            self.erika.print_string("Hallo zurück!")

        def save(self):
            '''Save to pastebin'''
            # this last line has the ;;:save command
            buffer = self.erika.input_lines_buffer
            lines = buffer[:len(self.erika.input_lines_buffer)-1:]
            p = Pastebin()
            paste_resp = p.paste(text='\n'.join(lines))
            write_to_screen(paste_resp)

        def help(self):
            '''Prints all Controll-Functions'''
            print('Printing help...')
    
        def typing(self, is_active):
            '''Typing echo on/of"'''
            print("Now typing is {}".format(is_active))
            self.erika.sender.set_keyboard_echo(is_active)
            write_to_screen("Now typing is {}".format(is_active))


    class Sender:

        def __init__(self, erika=None):
            self.erika = erika

        def alarm(self, duration=30):
            """Sound alarm for as long as possible"""
            if duration > 255:
                duration = 255
            self.set_keyboard_echo(False)
            self._print_raw("AA")
            self._print_raw(self._int_to_hex(duration))
            self.set_keyboard_echo(True)

        def _print_raw(self, data):
            """prints base16 formated data"""
            byte_data = binascii.unhexlify(data)
            print(byte_data)
            self.erika.uart.write(byte_data)

        def _print_smiley(self):
            """print a smiley"""
            self._print_raw('13')
            time.sleep(0.2)
            self._print_raw('1F')

        def set_keyboard_echo(self, is_active=True):
            if is_active:
                self._print_raw("92")
            else:
                self._print_raw("91")

        def _int_to_hex(self,value):
            hex_str = hex(value)[2:]
            hex_str = "0"+hex_str
            return hex_str[-2:]