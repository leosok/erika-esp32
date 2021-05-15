import paho.mqtt.client as mqtt
import json
import logging
from app.model import Textdata
from peewee import IntegrityError

logging.basicConfig()
logger = logging.getLogger("erika_mqqt_bridge")
logger.setLevel(logging.DEBUG)


def start_mqqt(mqqt_server, mqqt_user, mqqt_password, subscribe_to="erika/1/print", qos=1):
    # If you want to use a specific client id, use
    # mqttc = mqtt.Client("client-id")
    # but note that the client id must be unique on the broker. Leaving the client
    # id parameter empty will generate a random id for you.
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    #mqttc.on_connect = on_connect
    #mqttc.on_publish = on_publish
    #mqttc.on_subscribe = on_subscribe
    # Uncomment to enable debug messages
    # mqttc.on_log = on_log
    mqttc.username_pw_set(mqqt_user, password=mqqt_password)
    mqttc.connect(mqqt_server, 1883, 60)
    mqttc.subscribe(subscribe_to, qos)
    mqttc.loop_forever()


def on_message(mqttc, obj, msg):
  try:
    data = json.loads(msg.payload)
    logger.info(data)
    try:
      Textdata.create(content=data['line'], hashid=data['hashid'], line_number=data['lnum'])
    except IntegrityError:
      logger.info("Already saved line {}".format(data['line']))
  except ValueError as e:
    logger.info(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
 
  return True
    
def on_log(mqttc, obj, level, string):
    print(string)


# def on_publish(mqttc, obj, mid):
#     print("mid: " + str(mid))
# def on_subscribe(mqttc, obj, mid, granted_qos):
#     print("Subscribed: " + str(mid) + " " + str(granted_qos))

