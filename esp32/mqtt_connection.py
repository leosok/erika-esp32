# pylint: disable=unused-wildcard-import, method-hidden
# pyright: reportMissingImports=false, reportUnusedVariable=warning

import plugins
from utils.misc import file_lines_count
from lib.mqtt_as import MQTTClient, config
import uasyncio as asyncio
import time
from machine import Timer
from erika import Erika
from config.mqqt_config import MqqtConfig
from config.user_config import UserConfig
from utils.misc import status_led
import ubinascii
import machine
import gc
import json


class ErikaMqqt:
    ERIKA_STATE_OFFLINE = b'0'
    ERIKA_STATE_LISTENING = b'1'
    ERIKA_STATE_PRINTING = b'2'

    def __init__(self, erika:Erika, mqqt_id='erika', erika_id='1'):
        self.uuid = ubinascii.hexlify(machine.unique_id()).decode()

        self.erika = erika
        self.mqqt_id = b'{}_{}'.format(mqqt_id, self.uuid)
        self.erika_id = self.uuid
        self.client = None
        self.wifi_status_sprite = None
        self.plugins = []

        self.channel_status = self._get_channel_name(
            'status')  # erika/1/status
        self.channel_print = self._get_channel_name('print')  # erika/1/print
        self.channel_upload = self._get_channel_name(
            'upload')  # erika/1/upload
        self.channel_keystrokes = self._get_channel_name('keystrokes')
        self.channel_print_all = b'erika/print/all'

    def _get_channel_name(self, channel_name: str):
        return b'erika/{channel_name}/{erika_id}'.format(erika_id=self.uuid, channel_name=channel_name)

    async def start_mqqt_connection(self, wifi_status_sprite:Sprite=None, mqqt_connection_sprite:Sprite=None):
        # moved here, so erika is not started by itself.
        print("Starting MQQT Connection")

        # Define configuration
        config['subs_cb'] = self.sub_cb
        config['wifi_coro'] = self.wifi_han
        config['will'] = (self.channel_status,
                          self.ERIKA_STATE_OFFLINE, True, 0)
        config['connect_coro'] = self.conn_han
        config['keepalive'] = 120

        mqqt_config = MqqtConfig()
        user_config = UserConfig()

        config['server'] = mqqt_config.MQQT_SERVER
        config['user'] = mqqt_config.MQQT_USERNAME
        config['password'] = mqqt_config.MQQT_PASSWORD
        config['ssid'] = user_config.wlan_ssid
        config['wifi_pw'] = user_config.wlan_password

        config['client_id'] = self.mqqt_id
        config['ssl'] = True

        self.wifi_status_sprite = wifi_status_sprite
        self.mqqt_connection_sprite = mqqt_connection_sprite

        self.client = MQTTClient(config)

        try:
            await self.client.connect()
        except OSError:  # type: ignore
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

        for plugin in self.plugins:
            if plugin.topic in topic:
                plugin.on_message(topic=topic, msg=msg_str)

        if "print" in topic:
            # print("Got something to print...")
            linefeed = True
            if "all" in topic:
                if json.loads(msg_str)["sender"] == self.erika_id:
                    return  # break, if our erika is the sender
                msg_str = json.loads(msg_str)["text"]

            asyncio.create_task(self.erika.print_text(
                msg_str, linefeed=linefeed))
            # set status needs to be changed. Needs to be set in printer and checked by mqqt in some loop

    # Changes the status of this Erika on the erika/n/status channel
    # status: ERIKA_STATE_OFFLINE, ERIKA_STATE_LISTENING, ERIKA_STATE_PRINTING

    async def set_status(self, status):
        await self.client.publish(self.channel_status, status, retain=True)

    async def wifi_han(self, state):
        print('Wifi is ', 'up' if state else 'down')
        if state == True:
            self.wifi_status_sprite.on(3)
            self.mqqt_connection_sprite.show_frame(1)
        else:
            self.wifi_status_sprite.off()
            self.mqqt_connection_sprite.off()
        status_led(status=state)
        await asyncio.sleep_ms(30)

    # If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
    async def conn_han(self, client):
        self.mqqt_connection_sprite.off()
        print("Subscribing to Channels: {}, {}".format(
            self.channel_print, self.channel_print_all))
        await client.subscribe(topic=self.channel_print, qos=0)
        await client.subscribe(topic=self.channel_print_all, qos=0)
        self.mqqt_connection_sprite.on(on_frame=2)

        for plugin in self.plugins:
            if plugin.active:
                channel = self._get_channel_name(plugin.topic)
                print("Subscribing PLUGIN to Channel: {}".format(channel))
                await client.subscribe(topic=channel, qos=0)
        asyncio.create_task(self.set_status(self.ERIKA_STATE_LISTENING))

    # "Upload" a textfile via mqqt
    async def upload_text_file(self, filename='saved_lines.txt'):
        import uuid
        import json
        screen = self.erika.screen
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
            screen.show_progress(progress=i, max=file_line_count)
        f.close()
        process_time = round((time.ticks_ms() - start_time) / 1000)
        screen.write_to_screen(
            "Ok. {} in {}s".format(i, process_time), margin=5)

        EMAIL_FROM = 'electronic@erika-cloud.de'
        # send command to send the email
        command_json = {"cmd": "email",
                        "hashid": hashid,
                        "from": EMAIL_FROM,
                        "to": UserConfig().email_adress
                        }
        await self.client.publish(self.channel_upload, json.dumps(command_json), qos=1)

    async def send_keystroke(self, key="", channel=None):
        channel = channel or self.channel_keystrokes
        await self.client.publish(self.channel_keystrokes, key, qos=0)
        for plugin in self.plugins:
            if plugin.keylogging:
                await plugin.on_keystroke(key)
