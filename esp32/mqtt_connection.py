from utils.misc import file_lines_count
from lib.mqtt_as import MQTTClient, config
import uasyncio as asyncio
from utils.screen_utils import write_to_screen, show_progress
import time
from machine import Timer
from erika import Erika
from config import MqqtConfig, UserConfig


class ErikaMqqt:
    ERIKA_STATE_OFFLINE = b'0'
    ERIKA_STATE_LISTENING = b'1'
    ERIKA_STATE_PRINTING = b'2'

    def __init__(self, erika, mqqt_id='erika', erika_id='1'):
        self.channel_status = b'{client_id}/{erika_id}/status'.format(client_id=mqqt_id,
                                                                      erika_id=erika_id)  # erika/1/status
        self.channel_print = b'{client_id}/{erika_id}/print'.format(client_id=mqqt_id,
                                                                    erika_id=erika_id)  # erika/1/print
        # erika/upload
        self.channel_upload = b'{client_id}/upload'.format(client_id=mqqt_id)

        self.erika = erika
        self.mqqt_id = mqqt_id
        self.erika_id = erika_id
        self.client = None

    async def start_mqqt_connection(self):
        # moved here, so erika is not started by itself.
        print("Starting MQQT Connection")

        # Define configuration
        config['subs_cb'] = self.sub_cb
        config['wifi_coro'] = self.wifi_han
        config['will'] = (self.channel_status,
                          self.ERIKA_STATE_OFFLINE, True, 0)
        config['connect_coro'] = self.conn_han
        config['keepalive'] = 120

        
        config['server'] = MQQT_SERVER
        config['user'] = MQQT_USERNAME
        config['password'] = MQQT_PASSWORD
        config['ssid'] = WLAN_SSID
        config['wifi_pw'] = WLAN_PASSWORD

        config['client_id'] = self.mqqt_id
        # config['clean'] = False

        self.client = MQTTClient(config)

        try:
            await self.client.connect()
        except OSError:
            print('Connection failed.')
            print('Connection failed. Retrying.')
            await asyncio.sleep_ms(3000)
            asyncio.create_task(self.start_mqqt_connection())
            return

    # async def send_to_printer(self, text):
    #     await self.set_status(self.ERIKA_STATE_PRINTING)
    #     await self.erika.queue.put(text)
    #     await asyncio.sleep_ms(100)
    #     while self.erika.is_printing:
    #         await asyncio.sleep_ms(100)
    #     await self.set_status(self.ERIKA_STATE_LISTENING)

    def sub_cb(self, topic, msg, retained):
        msg_str = str(msg, 'UTF-8')
        print(topic + ":" + msg_str)

        if "show" in topic:
            write_to_screen(msg_str)
        if "print" in topic:
            print("Got something to print...")
            asyncio.create_task(self.erika.print_text(msg_str))
            # set status needs to be changed. Needs to be set in printer and checked by mqqt in some loop

    # Changes the status of this Erika on the erika/n/status channel
    # status: ERIKA_STATE_OFFLINE, ERIKA_STATE_LISTENING, ERIKA_STATE_PRINTING

    async def set_status(self, status):
        await self.client.publish(self.channel_status, status, retain=True)

    async def wifi_han(self, state):
        print('Wifi is ', 'up' if state else 'down')
        await asyncio.sleep_ms(30)

    # If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
    async def conn_han(self, client):
        print("Subscribing to Channel: {}".format(self.channel_print))
        await client.subscribe(topic=self.channel_print, qos=0)
        asyncio.create_task(self.set_status(self.ERIKA_STATE_LISTENING))

    # "Upload" a textfile via mqqt
    async def upload_text_file(self, filename='saved_lines.txt'):
        import uuid
        import json
        hashid = str(uuid.uuid4())[:8]

        file_line_count = file_lines_count(filename)
        start_time = time.ticks_ms()
        f = open(filename, 'r')
        i = 0
        for line in f:
            i += 1
            line_json = {
                "hashid": hashid,
                "line": '{}'.format(line.strip()),
                "lnum": b'{}'.format(i)
            }
            #print("line: {} {}".format(i, json.dumps(line_json)))
            await self.client.publish(self.channel_upload, json.dumps(line_json), qos=1)
            asyncio.sleep(0.05)
            show_progress(progress=i, max=file_line_count)
        f.close()
        process_time = round((time.ticks_ms() - start_time) / 1000)
        write_to_screen("Ok. {} in {}s".format(i, process_time), margin=5)

        # send command to send the email
        command_json = {"cmd": "email",
                        "hashid": hashid,
                        "from": EMAIL_FROM,
                        "to": EMAIL_TO
                        }
        await self.client.publish(self.channel_upload, json.dumps(command_json), qos=1)
