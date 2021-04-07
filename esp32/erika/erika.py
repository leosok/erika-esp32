

from erika import char_map
import time
from machine import UART, Pin
from erika import erica_encoder_decoder
import binascii
import uasyncio as asyncio
from primitives.queue import Queue
from utils.screen_utils import write_to_screen
from utils.umailgun import send_mailgun


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

        self.keyboard_echo = True
        # asyncio
        # self.start_receiver()

    # async def print_test(self, queue, counter):
    #     while True:
    #         counter += 1
    #         await asyncio.sleep(5)
    #         print('Should now print (print_test)')
    #         await queue.put(" Hallo{}. ".format(counter))

    def start_async_printer_and_receiver(self, loop):
        #loop = asyncio.get_event_loop()
        loop.create_task(self.receiver())
        print("Erika now listening to Keyboard async")
        loop.create_task(self.printer(self.queue))
        print("Erika now listening Print-Queue async")
        # loop.create_task(self.print_test(self.queue,0))
        # print('Erika Print_test startet')
        # loop.run_forever() <-- moved to main


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
            print("Running printer()")
            text = await queue.get()  # Blocks until data is ready
            print('QUEUE has something')

            swriter = asyncio.StreamWriter(self.uart, {})
            for char in text:
                sent = False
                while not sent:
                    print("RTS {}".format(self.rts.value()))
                    if self.rts.value() == 0:
                        # Erika is ready
                        #print(char, end=' : ')
                        char_encoded = self.ddr_2_ascii.encode(char)
                        # print(char_encoded)
                        swriter.write(char_encoded)
                        await swriter.drain()
                        await asyncio.sleep_ms(20)
                        sent = True
                    else:
                        print("pausing")
                        sent = False
                        await asyncio.sleep_ms(20)
                        #await asyncio.sleep(0.5)
                #await asyncio.sleep(0.5)
            # if linefeed:
            #     newline = self.ddr_2_ascii.encode('\n')
            #     swriter.write(newline)
            #     await swriter.drain()
   
            print('printer done for now')
            
    
    def print_old(self, text: str, linefeed=True):
      
      # output = ''
      # lines = self.string_to_lines(text)
      # print(lines)
      # for line in lines:
      
        sent = False
        while not sent:
            for char in text:   
                print(self.rts.value())
                if self.rts.value() == 0:
                    # Erika is ready
                    char_encoded = self.ddr_2_ascii.encode(char)
                    self.uart.write(char_encoded)
                else:
                    time.sleep(0.5)
            sent=True

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



    class ActionController:

        def __init__(self, erika=None):
            self.erika = erika
            self.action_promt_string =erika.ACTION_PROMT_STRING
        
        actions = {
            "hallo": "Print Hallo Welt",
            "save": "Save Buffer to Pastee",
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

        def send(self):
            '''Send as Mail'''
            # this last line has the ;;:save command
            buffer = self.erika.input_lines_buffer
            lines = buffer[:len(self.erika.input_lines_buffer)-1:]
            
            mail_text = '\n'.join(lines)
            date_str = "/".join([str(t) for t in time.localtime()[0:3]])
            mail_subject = "Erika {}".format(date_str)         
           
            send_mailgun(mail_subject=mail_subject, mail_text=mail_text)
            write_to_screen('Mailed {} lines'.format(len(lines)))
            # empty the buffer, so next mail will only include relevant text
            self.erika.input_lines_buffer = []

        def help(self):
            '''Prints all Controll-Functions'''
            print('Printing help...')
    
        def typing(self, is_active):
            '''Typing echo on/of"'''
            print("Typing: {}".format(is_active))
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