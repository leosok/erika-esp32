from umqtt2.robust2 import MQTTClient
from screen_utils import write_to_screen
import time
from machine import Timer
from erika import Erika
from .secrets import MQQT_PASSWORD, MQQT_SERVER, MQQT_USERNAME

MQQT_CLIENT_ID = "erika"
# This will be used for the status of your Erika on the MQQT-Broker.
MQQT_ERIKA_ID = 1

ERIKA_STATE_OFFLINE = b'0'
ERIKA_STATE_LISTENING = b'1'
ERIKA_STATE_PRINTING = b'2'

ERIKA_CHANNEL_STATUS = b'{client_id}/{erika_id}/status'.format(client_id=MQQT_CLIENT_ID,
                                                               erika_id=MQQT_ERIKA_ID)  # erika/1/status

ERIKA_CHANNEL_PRINT= b'{client_id}/{erika_id}/status'.format(client_id=MQQT_CLIENT_ID,
                                                               erika_id=MQQT_ERIKA_ID)  # erika/1/print                                                

client = False
erika = Erika()


def sub_cb(topic, msg, retained, duplicate):

    print(topic + ":" + msg)
    msg_str = str(msg, 'UTF-8')
    if "show" in topic:
        write_to_screen(msg_str)
    if "print" in topic:
        print("Got something to print...")
        set_status(ERIKA_STATE_PRINTING)
        erika.print_string(msg_str + '\n')
        set_status(ERIKA_STATE_LISTENING)


def check_channel(Timer):

    global client

    # At this point in the code you must consider how to handle
    # connection errors.  And how often to resume the connection.
    if client.is_conn_issue():
        while client.is_conn_issue():
            # If the connection is successful, the is_conn_issue
            # method will not return a connection error.
            client.reconnect()
        else:
            # set status of Erika to "listening"
            set_status(ERIKA_STATE_LISTENING)
            client.resubscribe()

    client.check_msg()

# Will start a connection to the mqtt-broker using
# check_msg_interval: integer, milliseconds

# Changes the status of this Erika on the erika/n/status channel
# status: ERIKA_STATE_OFFLINE, ERIKA_STATE_LISTENING, ERIKA_STATE_PRINTING
def set_status(status):
    client.publish(ERIKA_CHANNEL_STATUS, status, retain=True)
    return True


def start_mqqt_connection(check_msg_interval=5000):

    global client

    print("Starting MQQT Connection")

    client = MQTTClient(client_id=MQQT_CLIENT_ID,
                        server=MQQT_SERVER,
                        port=1883,
                        user=MQQT_USERNAME,
                        password=MQQT_PASSWORD,
                        keepalive=20
                        )

    # Set Last Will to "offline"
    client.set_last_will(ERIKA_CHANNEL_STATUS, ERIKA_STATE_OFFLINE, retain=True)
    client.set_callback(sub_cb)

    client.connect()

    # set status of Erika to "listening"
    set_status(ERIKA_STATE_LISTENING)
    client.subscribe(topic=ERIKA_CHANNEL_PRINT)

    # This Timer will check for MQQT-Messages
    timer = Timer(0)
    timer.init(period=check_msg_interval,
               mode=Timer.PERIODIC, callback=check_channel)
