from utils.screen_utils import write_to_screen
import time
from machine import Timer
from erika import Erika
from secrets import MQQT_PASSWORD, MQQT_SERVER, MQQT_USERNAME, WLAN_SSID, WLAN_PASSWORD
import uasyncio as asyncio
from mqtt_as import MQTTClient, config



MQQT_CLIENT_ID = "erika"
# This will be used for the status of your Erika on the MQQT-Broker.
MQQT_ERIKA_ID = 1

ERIKA_STATE_OFFLINE = b'0'
ERIKA_STATE_LISTENING = b'1'
ERIKA_STATE_PRINTING = b'2'

ERIKA_CHANNEL_STATUS = b'{client_id}/{erika_id}/status'.format(client_id=MQQT_CLIENT_ID,
                                                               erika_id=MQQT_ERIKA_ID)  # erika/1/status

ERIKA_CHANNEL_PRINT= b'{client_id}/{erika_id}/print'.format(client_id=MQQT_CLIENT_ID,
                                                               erika_id=MQQT_ERIKA_ID)  # erika/1/print                                                

erika = None


async def send_to_printer(text):
    await erika.queue.put(text)


def sub_cb(topic, msg, retained):
    global erika

    msg_str = str(msg, 'UTF-8')
    print(topic + ":" + msg_str)
    
    if "show" in topic:
        write_to_screen(msg_str)
    if "print" in topic:
        print("Got something to print...")
        asyncio.create_task(send_to_printer(msg_str))
        # set status needs to be changed. Needs to be set in printer and checked by mqqt in some loop
        

# Will start a connection to the mqtt-broker using
# check_msg_interval: integer, milliseconds


# Changes the status of this Erika on the erika/n/status channel
# status: ERIKA_STATE_OFFLINE, ERIKA_STATE_LISTENING, ERIKA_STATE_PRINTING
async def set_status(client, status=1):
    global erika
    status = ERIKA_STATE_PRINTING if erika.is_printing else ERIKA_STATE_LISTENING
    await client.publish(ERIKA_CHANNEL_STATUS, status, retain=True)
    asyncio.sleep(1)

async def wifi_han(state):
    print('Wifi is ', 'up' if state else 'down')
    await asyncio.sleep_ms(30)

# If you connect with clean_session True, must re-subscribe (MQTT spec 3.1.2.4)
async def conn_han(client):
    print("Subscribing to Channel: {}".format(ERIKA_CHANNEL_PRINT))
    await client.subscribe(topic=ERIKA_CHANNEL_PRINT, qos=0)
    asyncio.create_task(set_status(client))

async def start_mqqt_connection(the_erika):
    global erika
    erika = the_erika

    # moved here, so erika is not started by itself.
    print("Starting MQQT Connection")

    # Define configuration
    config['subs_cb'] = sub_cb
    config['wifi_coro'] = wifi_han
    config['will'] = (ERIKA_CHANNEL_STATUS, ERIKA_STATE_OFFLINE, True, 0)
    config['connect_coro'] = conn_han
    config['keepalive'] = 120
    
    config['server'] = MQQT_SERVER
    config['user'] = MQQT_USERNAME
    config['password'] = MQQT_PASSWORD
    config['ssid'] = WLAN_SSID
    config['wifi_pw'] = WLAN_PASSWORD

    config['client_id'] = MQQT_CLIENT_ID
    # config['clean'] = False

    client = MQTTClient(config)

    try:
        await client.connect()
    except OSError:
        print('Connection failed.')
        return