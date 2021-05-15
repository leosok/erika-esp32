# pylint: disable=unused-wildcard-import, method-hidden

from erika import char_map
import time
from machine import UART, Pin
from erika import erica_encoder_decoder
import binascii
import uasyncio as asyncio
from primitives.queue import Queue
from utils.screen_utils import write_to_screen
from utils.umailgun import Mailgun, CONFIG_MY_EMAIL, MAILGUN_API_KEY, MAILGUN_API_URL

# For more stuff see:
# https://github.com/Chaostreff-Potsdam/erika3004/blob/5886ae8af26bc73716dcc848c19a5fa46c7c59c4/erika/erika.py


class Erika:
    DEFAULT_BAUD_RATE = 1200
    DEFAULT_LINE_LENGTH = 60
    DEFAULT_DELAY = 0.02
    RTS_PIN = 22
    CTS_PIN = 21
    TEMP_LINES_FILE = "saved_lines.txt"
    # Using an Array for ACTION_PROMT_STRING, because Char does not work with REL
    ACTION_PROMT_CHARS = ["REL","REL","REL"]
    ACTION_PROMT_STRING = ''.join(ACTION_PROMT_CHARS)

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
        # Without CTS to low, Erika will not send data
        cts = Pin(Erika.CTS_PIN, Pin.OUT)
        cts.off

        self.sender = self.Sender(self)
        self.action_controller = self.ActionController(self)
        # Queue for the printer
        self.queue = Queue()
        # will be used for MQQT-Status
        self.is_printing=False

        self.keyboard_echo = True
        # this is a way to upload files:
        self.mqqt_client = None

    # async def print_test(self, queue, counter):
    #     while True:
    #         counter += 1
    #         await asyncio.sleep(5)
    #         print('Should now print (print_test)')
    #         await queue.put(" Hallo{}. ".format(counter))

    
    async def receiver(self):
        sreader = asyncio.StreamReader(self.uart)
        while True:
            tmp_bytes = await sreader.read(1)
            decoded_char = self.ddr_2_ascii.decode(tmp_bytes) 
            # print(self.ACTION_PROMT_STRING[-1:][0])   
            # print(decoded_char)        
            if decoded_char=='\n':
                current_line = self.input_line_buffer
                print(current_line)
                self.input_lines_buffer.append(current_line)
                if self.action_controller.check_for_action(current_line) == False:
                    self._save_lines_to_file(current_line)
                self.input_line_buffer = ''
            elif decoded_char == 'DEL':
                # remove last character, if DEL was hit
                self.input_line_buffer = self.input_line_buffer[:-1]
            elif decoded_char == self.ACTION_PROMT_CHARS[-1:][0]:
                self.input_line_buffer += decoded_char
                # If we hit the last Char of ACTION_PROMT_STRING check if the rest was typed
                last_chars = self.input_line_buffer[-len(self.ACTION_PROMT_STRING):]
                if last_chars == self.ACTION_PROMT_STRING:
                    self.action_controller.start_action_promt()
            else:
                self.input_line_buffer += decoded_char

    async def printer(self, queue, linefeed=True):
        while True:
            text = await queue.get()  # Blocks until data is ready
            print('Printer found text in Queue')
            self.is_printing = True
            swriter = asyncio.StreamWriter(self.uart, {})
            lines = self.string_to_lines(text)  
            print(lines)          
            for line in lines:
                print(line)
                for char in line:
                    sent = False
                    while not sent:
                        # print("RTS {}".format(self.rts.value()))
                        if self.rts.value() == 0:
                            # Erika is ready
                            #print(char, end=' : ')
                            char_encoded = self.ddr_2_ascii.encode(char)
                            if len(char) == 0:
                                # char could not be decoded
                                break
                            swriter.write(char_encoded)
                            await swriter.drain()
                            await asyncio.sleep_ms(30)
                            sent = True
                        else:
                            # print("pausing")
                            sent = False
                            await asyncio.sleep_ms(40)

            self.is_printing = False
            print('printer done for now')
            

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

    

    def string_to_lines(self, text, max_length=DEFAULT_LINE_LENGTH):
        '''
        Returns an array of lines with a max_length of DEFAULT_LINE_LENGTH
        All newlines from the original lines are used
        in case a line is to long, an extra newline is inserted
        '''
        newline = '\n'
        all_lines = text.split(newline)
        lines = []
        for aline in all_lines:
            words = aline.split()
            tmp_line = ''

            # If the text is less than a line, return it
            if len(text) <= max_length:
                lines.append(text + newline)
            else:
                # else split to lines
                for word in words:
                    next = ' '.join([tmp_line, word])
                    if len(next) <= max_length:
                        tmp_line = next
                    else:
                        lines.append(tmp_line.strip() + newline)
                        tmp_line = word

                # for the last words
                lines.append(tmp_line.strip() + newline)
        return lines    


    def _save_lines_to_file(self, lines, filename=TEMP_LINES_FILE):
        f = open(filename, 'a')
        # if it's just one line fake an array
        if type(lines) is str:
            lines = [lines]
        # save to file
        for line in lines:
            f.write(line + '\n')
        f.close()



    class ActionController:

        def __init__(self, erika=None):
            self.erika = erika
            self.action_promt_string =erika.ACTION_PROMT_STRING
        
        actions = {
            "hallo": "Print Hallo Welt",
            "save": "Mail to User",
            "help": "Prints this info",
            "typing": "Turn echo ON/OFF",
            "send": "send as mail"
        }

        def start_action_promt(self):
            write_to_screen("Enter Action")
            self.erika.sender.alarm()
            self.erika.sender.set_keyboard_echo(False)  

        
        def check_for_action(self, input:str):
            if self.action_promt_string in input:
                c_string_start = input.rfind(self.action_promt_string) + len(self.action_promt_string)
                control_string = input[-len(input) + c_string_start:] # the last characters after ACTION_PROMT_STRING
                # Keyboard was off for "start_action_promt", set it back to original state
                self.erika.sender.set_keyboard_echo(self.erika.keyboard_echo) 
                write_to_screen("Action: {}".format(control_string))       
                self.action(control_string)
            else:
                return False

        def action(self, action_str:str):
            action_str = action_str.replace(' ','_')
            print("Action: {}".format(action_str))
            try:
                loop = asyncio.get_event_loop()
                if '_on' in action_str.lower():
                    method_name = action_str[:-len('_on')]
                    method_to_call = getattr(self,method_name)
                    method_attr = True
                    loop.create_task(method_to_call(method_attr))
                elif '_off' in action_str.lower():
                    method_name = action_str[:-len('_off')]
                    method_to_call = getattr(self, method_name)
                    method_attr = False
                    loop.create_task(method_to_call(method_attr))
                else:
                    # TODO: everything to Async!
                    method_to_call = getattr(self, action_str)
                    loop.create_task(method_to_call())         
               
            except AttributeError:
                print("Could not execute '{}'".format(action_str))

        async def hallo(self):
            '''Prints a "hello"'''
            time.sleep(1)
            await self.erika.queue.put('Hallo, Du!')

        async def send(self):
            '''Send as Mail'''
            # this last line has the ;;:save command
            await self.erika.mqqt_client.upload_text_file(self.erika.TEMP_LINES_FILE)
            self.erika.input_lines_buffer = []

        async def clear_lines(self):
            '''resets the temp file'''
            # this last line has the ;;:save command
            open(self.erika.TEMP_LINES_FILE, "w").close()
            write_to_screen("Tempfile clear.")


        def help(self):
            '''Prints all Controll-Functions'''
            print('Printing help...')
    
        async def typing(self, is_active):
            '''Typing echo on/of"'''
            print("Typing is: {}".format(is_active))
            self.erika.sender.set_keyboard_echo(is_active)
            write_to_screen("Now typing is {}".format(is_active))


    class Sender:

        def __init__(self, erika=None):
            self.erika = erika

        def alarm(self, duration=30):
            """Sound alarm for as long as possible"""
            if duration > 255:
                duration = 255
            # Beep will only come if keyboard_echo is off
            self.set_keyboard_echo(False)
            self._print_raw("AA")
            self._print_raw(self._int_to_hex(duration))
            # Set keyboard_echo to original state
            self.set_keyboard_echo(self.erika.keyboard_echo)

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

        def _newline(self):
            self._print_raw('77')


        def set_keyboard_echo(self, is_active=True):
            if is_active:
                self._print_raw("92")
                time.sleep(0.2)
            else:
                self._print_raw("91")
                time.sleep(0.2)

        def _int_to_hex(self,value):
            hex_str = hex(value)[2:]
            hex_str = "0"+hex_str
            return hex_str[-2:]