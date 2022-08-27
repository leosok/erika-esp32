# For relative imports to work in Python 3.6
import sys;
from json import JSONDecodeError

sys.path.append("..")
from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD, TWIITTER_BEARER_TOKEN
import uuid
import paho.mqtt.client as mqtt
import json
import logging
from models import Textdata, Typewriter
from peewee import IntegrityError, DoesNotExist
from datetime import datetime

logging.basicConfig()
logger = logging.getLogger("erika_mqqt_bridge")
logger.setLevel(logging.DEBUG)


class ErikaMqqt:

    def __init__(self, mqqt_server=MQQT_SERVER, mqqt_user=MQQT_USERNAME, mqqt_password=MQQT_PASSWORD):

        # If you want to use a specific client id, use
        # mqttc = mqtt.Client("client-id")
        # but note that the client id must be unique on the broker. Leaving the client
        # id parameter empty will generate a random id for you.
        self.mqttc = mqtt.Client()
        self.mqttc.on_message = self.on_message

        # This will make mqttc re-subscribe after re-connect
        self.mqttc.on_connect = self.on_connect
        self.mqttc.on_disconnect = self.on_disconnect
        self.mqttc.on_subscribe = self.on_subscribe

        # Uncomment to enable debug messages
        # self.mqttc.on_log = self.on_log
        self.mqttc.username_pw_set(mqqt_user, password=mqqt_password)
        self.mqttc.connect(mqqt_server, 1883, 60)

    def on_connect(self, mqttc, userdata, flags, rc, properties=None):
        print("connecting to MQQT....")
        print("(Re-)subscribing")
        print("Connected with result code " + str(rc))
        self.subscribe()

    def on_subscribe(self, mqqtc, userdata, mid, rc):
        if rc[0] == 0:
            print(f"Could not subscribe: '{str(mid)}'")
        else:
            print(f"Subscription '{str(mid)}' worked!")

    def subscribe(self, subscribe_to="erika/#", qos=1):
        print("Subscribing....")
        self.mqttc.subscribe(subscribe_to, qos)

    def run_forever(self):
        self.mqttc.loop_forever()

    def on_message(self, mqttc, obj, msg):
        try:
            data = json.loads(msg.payload)
            logger.info(data)
        except JSONDecodeError:
            logger.debug("Not a json")
        typewriter_id = msg.topic.split('/')[2]
        msg_type = msg.topic.split('/')[1]

        logger.info(msg.topic.split('/'))

        if msg_type == "status":
            logger.info(f"Status of Typewriter {typewriter_id} changed to {msg.payload}")
            try:
                typewriter = Typewriter.get(Typewriter.uuid == typewriter_id)
                if typewriter.status < int(msg.payload):
                    # status was 0 is 1 now
                    typewriter.print_mails()
                typewriter.status = int(msg.payload)
                typewriter.save()
            except DoesNotExist as e:
                logger.info(e)

        # Execute Commands from Erika
        if msg_type == "upload":               
            if "cmd" in data:
                if data["cmd"] == "email":
                    subject = f'Erika Text {datetime.now().strftime("%d.%m.%Y")}'
                    content = Textdata.as_fulltext(data['hashid'])
                    
                    from utils.mail_utils import send_email
                    return send_email(data['from'], data['to'], subject, content)
            else:
                Textdata.create(content=data['line'], hashid=data['hashid'], line_number=data['lnum'])

        if msg_type == "twitter":
            from utils.mail_utils import print_on_erika
            from plugins.twitter_plugin import get_new_tweet
            typewriter = Typewriter.get(Typewriter.uuid == typewriter_id)
            if "cmd" in data:
                if data["cmd"] == "get_tweets":
                    tweet = get_new_tweet(bearer_token=TWIITTER_BEARER_TOKEN, query_str=data['query'], since_id=data['last_tweet_id'])
                    if tweet:
                        # print_str = f"{tweet.text}\n"
                        self.mqttc.publish(f'{msg.topic}', json.dumps(tweet.__dict__))
                                 
                    
        return True

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def on_disconnect(self, mqttc, userdata, rc):
        print(f"on_disconnect: {rc}")
        if rc != 0:
            print("Unexpected MQTT disconnection. Will auto-reconnect")

# def on_publish(mqttc, obj, mid):
#     print("mid: " + str(mid))
# def on_subscribe(mqttc, obj, mid, granted_qos):
#     print("Subscribed: " + str(mid) + " " + str(granted_qos))
