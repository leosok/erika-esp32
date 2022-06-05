# pylint: disable=unused-wildcard-import, method-hidden

from erika import char_map
import time
from machine import UART, Pin, unique_id, reset
from erika import erica_encoder_decoder
import binascii
import uasyncio as asyncio
from lib.primitives.queue import Queue
# from utils.umailgun import Mailgun, CONFIG_MY_EMAIL, MAILGUN_API_KEY, MAILGUN_API_URL

# For more stuff see:
# https://github.com/Chaostreff-Potsdam/erika3004/blob/5886ae8af26bc73716dcc848c19a5fa46c7c59c4/erika/erika.py


class Erika:
    DEFAULT_BAUD_RATE = 1200
    DEFAULT_DELAY = 0.02
    RTS_PIN = 22
    CTS_PIN = 21
    RX_PIN = 5
    TX_PIN = 17

    TEMP_LINES_FILE = "saved_lines.txt"
    
    # Using an Array for ACTION_PROMT_STRING, because Char does not work with REL
    ACTION_PROMT_CHARS = ["REL", "REL", "REL"]
    ACTION_PROMT_STRING = ''.join(ACTION_PROMT_CHARS)

    # Paper
    DEFAULT_LINE_LENGTH = 60
    LINES_PER_PAGE = {
        'LINE_SPACING_10' : 60, 
        'LINE_SPACING_15': 40, 
        'LINE_SPACING_20': 30
        }
    CHAR_SPACING = 0 # 0 = 10, 1 = 12 on the slider

    def __init__(self, rts_pin=RTS_PIN, cts_pin=CTS_PIN, rx_pin=RX_PIN, tx_pin=TX_PIN, screen=None):
        print("Erika loading. rts:{} cts:{} rx:{} tx:{}".format(rts_pin,cts_pin, rx_pin, tx_pin))
        # line_buffer will be filled until "Return" is hit
        self.input_line_buffer = ''
        # lines_buffer will save the whole texte before doing sth with it.
        self.input_lines_buffer = []

        # Remember Rx/Tx are opposed to Pins at the typewriter:
        # If your Rx is on Pin 5, connect it to Tx on the typewriter (B13)
        self.rx = rx_pin
        self.tx = tx_pin

        self.uart = self.start_uart()
        self.ddr_2_ascii = erica_encoder_decoder.DDR_ASCII()
        # It is important to PULL_DOWN the RTS_PIN, to get a reading! (0=OK, 1=busy, please wait)
        self.rts = Pin(rts_pin)
        self.rts.init(self.rts.IN, self.rts.PULL_DOWN)
        # Without CTS to low, Erika will not send data
        cts = Pin(cts_pin, Pin.OUT)
        cts.off

        self.sender = self.Sender(self)
        self.action_controller = self.ActionController(self)
        # Queues for the printer + promts
        self.queue_print = Queue()
        self.queue_prompt = Queue()

        # will be used for MQQT-Status
        self.is_printing = False
        self.is_prompting = False

        self.keyboard_echo = True
        self.mqqt_send_keystrokes = True
        
        # page settings
        self.lines_per_page = self.LINES_PER_PAGE['LINE_SPACING_20']
        self.line_on_page = 0

        # this is a way to upload files:
        self.mqqt_client = None
        self.uuid = binascii.hexlify(unique_id()).decode()

        # for using screen
        self.screen = screen

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
            if decoded_char == '\n':
                current_line = self.input_line_buffer
                print(current_line)
                self.input_lines_buffer.append(current_line)
                if self.mqqt_send_keystrokes:
                    await self.mqqt_client.send_keystroke(key='\n')
                # if we are waiting for a response from a user-promt
                if self.is_prompting:
                    print("promting... current_line is {}".format(current_line))
                    if not current_line:
                        print("current_line is emtry")
                        # This is when waiting for paper
                        await self.queue_prompt.put("ok")
                    else:
                        await self.queue_prompt.put(current_line)
                # check if this is an "action"
                elif self.action_controller.check_for_action(current_line) == False:
                    self._save_lines_to_file(current_line)
                self.input_line_buffer = ''
            elif decoded_char == 'DEL':
                # remove last character, if DEL was hit
                self.input_line_buffer = self.input_line_buffer[:-1]
                if self.mqqt_send_keystrokes:
                    await self.mqqt_client.send_keystroke(key='DEL')
            elif decoded_char == self.ACTION_PROMT_CHARS[-1:][0]:
                self.input_line_buffer += decoded_char
                # If we hit the last Char of ACTION_PROMT_STRING check if the rest was typed
                last_chars = self.input_line_buffer[-len(
                    self.ACTION_PROMT_STRING):]
                if last_chars == self.ACTION_PROMT_STRING:
                    self.action_controller.start_action_promt()
            elif decoded_char in char_map.page_controls:
                try:
                    self.lines_per_page = self.LINES_PER_PAGE[decoded_char]
                    print("Changing lines_per_page to {}".format(self.lines_per_page))
                except:
                    pass
            else:
                self.input_line_buffer += decoded_char
                if self.mqqt_send_keystrokes:
                    await self.mqqt_client.send_keystroke(key=decoded_char)


    async def printer(self, queue):
        while True:
            text, linefeed = await queue.get()  # Blocks until data is ready
            self.is_printing = True
            swriter = asyncio.StreamWriter(self.uart, {})
            # When it is just a key, string_to_lines
            if len(text) == 1:
                print('Printer printing a key: {}'.format(text))
                lines = [text]
            else:
                print('Printer found text in Queue. Linefeed is {}'.format(linefeed))
                lines = self.string_to_lines(text=text, linefeed=linefeed)
            for idx, line in enumerate(lines):
                print("{}/{}: {}".format(idx, len(lines), line))                
                if self.line_on_page >= self.lines_per_page:
                    print("Asking for new paper")
                    await self.ask_for_paper()
                    # This is to "suck in" the new paper.
                    # TODO: make this an option
                    self.sender.paper_feed()
                else:
                    self.line_on_page += 1
                for char in line:
                    sent = False
                    while not sent:
                        #print("RTS {}".format(self.rts.value()))
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
            self.line_on_page = 0
            print('printer done for now')

    def start_uart(self, rx=RX_PIN, tx=TX_PIN, baud=1200):
        uart = UART(2, baud)
        uart.init(baud, bits=8, parity=None, stop=1, rx=self.rx, tx=self.tx)
        print("uart started")
        return uart

    async def print_text(self, text, linefeed=True):
        '''
        Prints a text on the Erika
        '''
        await self.queue_print.put((text, linefeed))
        await asyncio.sleep_ms(100)
        while self.is_printing:
            await asyncio.sleep_ms(100)
        return True

    async def ask(self, promt: str, ask_bool: bool = False, only_enter=False) -> str:
        """
        Prints a prompt and returns the answer from the user as string

        only_enter(bool): used for asked_for_paper. Just waits for an Enter and returnes
        """
        positives = ['y', 'j', 'ja', 'ok', 'yes']
        negatives = ['n', 'nein', 'no']

        bool_promt_txt = ' (y/n) ' if ask_bool else ''
        promt_txt = promt + bool_promt_txt + ': '
        
        if not only_enter:
            await self.print_text(promt_txt, linefeed=False)
        print("Waiting for User-Input: {}".format(promt_txt))
        self.is_prompting = True
        user_answer = await self.queue_prompt.get()
        self.is_prompting = False
        print("User answered: {}".format(user_answer))
        if not ask_bool:
            return user_answer
        else:
            is_positiv = user_answer.lower() in positives
            is_negativ = user_answer.lower() in negatives
            if is_positiv:
                print("bool-answer positive")
                return True
            elif is_negativ:
                print("bool-answer negative")
                return False
            else:
                print("Bool-Question was answered with {}".format(user_answer))
                return await self.ask(promt="Fehler. Bitte mit 'Ja' oder 'Nein' antworten", ask_bool=True)

    
    async def ask_for_paper(self):
        """
        Promt User to enter Paper and press Enter
        """
        self.sender.alarm()
        #self.sender.set_keyboard_echo(False)
        self.screen.write_to_screen("Papier einlegen", line=3, centered=True)
        self.screen.write_to_screen(" und ENTER", line=4, centered=True)   
        self.is_prompting = True
        await self.ask("",only_enter=True) # just wait for the Enter
        self.line_on_page = 0

    def string_to_lines(self, text, max_length=DEFAULT_LINE_LENGTH, linefeed=True):
        '''
        Returns an array of lines with a max_length of DEFAULT_LINE_LENGTH
        All newlines from the original lines are used
        in case a line is to long, an extra newline is inserted
        '''
        newline = '\n'
        if linefeed:
            last_char = newline
        else:
            last_char = ''
        all_lines = text.split(newline)
        lines = []
        for aline in all_lines:
            words = aline.split()
            tmp_line = ''

            # If the text is less than a line, return it
            if len(aline) <= max_length:
                lines.append(aline + last_char)
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
                lines.append(tmp_line.strip() + last_char)
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

        def __init__(self, erika:Erika = None): #type: ignore
            self.erika = erika
            self.action_promt_string = erika.ACTION_PROMT_STRING

        docs = {
            "p": "Papiereinzug",
            "hallo": "Print Hallo Welt",
            "hilfe": "Diese Hilfe drucken",
            "typing": "Tastatur ON/OFF",
            "send": "Gesendete Texte als Email an mich senden",
            "clear": "Löscht die zwischengespeicherten Texte",
            "reset": "Setzt alle Einstellungen (z.B. Wifi) zurück und startet neu."
        }

        def start_action_promt(self):
            self.erika.screen.write_to_screen("Enter Action")
            self.erika.sender.alarm()
            self.erika.sender.set_keyboard_echo(False)
            self.erika.mqqt_send_keystrokes = False

        def check_for_action(self, input: str):
            if self.action_promt_string in input:
                c_string_start = input.rfind(
                    self.action_promt_string) + len(self.action_promt_string)
                # the last characters after ACTION_PROMT_STRING
                control_string = input[-len(input) + c_string_start:]
                # Keyboard was off for "start_action_promt", set it back to original state
                self.erika.sender.set_keyboard_echo(self.erika.keyboard_echo)
                self.erika.screen.write_to_screen("Action: {}".format(control_string))
                self.action(control_string)
            else:
                return False

        def action(self, action_str: str):
            action_str = action_str.replace(' ', '_')
            print("Action: {}".format(action_str))
            try:
                loop = asyncio.get_event_loop()
                if '_on' in action_str.lower():
                    method_name = action_str[:-len('_on')]
                    method_to_call = getattr(self, method_name)
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

            except AttributeError: # type: ignore
                print("Could not execute '{}'".format(action_str))

        async def p(self):
            info = '''feeds paper'''
            self.erika.sender.paper_feed()
            return info

        async def keycast(self, is_active):
            '''Send every key typed to MQQT'''
            self.erika.mqqt_send_keystrokes = is_active
            self.screen.write_to_screen("Keycast: {}".format(is_active))

        async def hallo(self):
            info = '''Prints a "hello"'''
            asyncio.sleep(1)
            await self.erika.print_text('Hallo, Du!')
            return info

        async def send(self):
            '''Send as Mail'''
            # this last line has the ;;:save command
            await self.erika.mqqt_client.upload_text_file(self.erika.TEMP_LINES_FILE)
            self.erika.input_lines_buffer = []

        async def clear(self):
            '''resets the temp file'''
            # this last line has the ;;:save command
            open(self.erika.TEMP_LINES_FILE, "w").close()
            self.erika.screen.write_to_screen("Tempfile clear.")

        async def reset(self):
            '''deletes User-config of this Erika'''
            from config.configurator import UserConfig
            result = UserConfig().delete()
            self.erika.screen.write_to_screen("Reset: {}".format(result))
            reset()

        async def typing(self, is_active):
            '''Typing echo on/off"'''
            print("Typing: {}".format(is_active))
            self.erika.sender.set_keyboard_echo(is_active)
            self.erika.screen.write_to_screen("Typing: {}".format(is_active))

        async def hilfe(self):
            parent_class = self
            method_list = [func for func in dir(parent_class) if \
                callable(getattr(parent_class, func)) and not func.startswith('_')]
            print(method_list)
            help_str = 'Funktionen der Erika.\n\n 3 x Taste REL drücken, Funktion eingeben, dann Enter.\n\n'
            for method in method_list:
                if self.docs.get(method):
                    # ignore all methods we did not document
                    help_str += ' --- ' + method.upper() + ' ---' + '\n'
                    help_str += self.docs.get(method) + '\n'
                    help_str += '\n'
            
            await self.erika.print_text(help_str)


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

        def _print_char(self, char):
            byte_data = self.erika.ddr_2_ascii.encode(char)
            self.erika.uart.write(byte_data)
            time.sleep(0.2)

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

        def paper_feed(self, steps = 140):
            self._print_raw(steps * "75")
            time.sleep(0.2)

        def _int_to_hex(self, value):
            hex_str = hex(value)[2:]
            hex_str = "0"+hex_str
            return hex_str[-2:]
