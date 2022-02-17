import paho.mqtt.client as mqtt
import json
import logging
from erika_cloud.models import Textdata
from erika_cloud.utils.mail_utils import send_email
from peewee import IntegrityError
from datetime import datetime

logging.basicConfig()
logger = logging.getLogger("erika_mqqt_bridge")
logger.setLevel(logging.DEBUG)

class ErikaMqqt:

  def __init__(self, mqqt_server, mqqt_user, mqqt_password):
    
    # If you want to use a specific client id, use
    # mqttc = mqtt.Client("client-id")
    # but note that the client id must be unique on the broker. Leaving the client
    # id parameter empty will generate a random id for you.
    self.mqttc = mqtt.Client()
    self.mqttc.on_message = self.on_message
    # mqttc.on_publish = on_publish
    self.mqttc.on_subscribe = self.on_subscribe
    # Uncomment to enable debug messages
    # self.mqttc.on_log = self.on_log
    self.mqttc.username_pw_set(mqqt_user, password=mqqt_password)
    self.mqttc.connect(mqqt_server, 1883, 60)
    
    # This will make mqttc re-subscribe after re-connect
    self.mqttc.on_connect =self.on_connect
    self.mqttc.on_disconnect =self.on_disconnect

  def on_connect(self, mqttc, userdata, flags, rc, properties=None):
    print("connecting to MQQT....")
    print("(Re-)subscribing")
    self.subscribe()

  def on_subscribe(self, mqqtc, userdata, mid, rc):
    print("Subscribing....")
    if rc != 0:
      print(f"Could not subscribe: '{str(mid)}'")
    else:
      print(f"Subscription '{str(mid)}' worked!")

  def subscribe(self, subscribe_to="erika/upload", qos=1):
    self.mqttc.subscribe(subscribe_to, qos)

  def run_forever(self):
    self.mqttc.loop_forever()

  def on_message(self, mqttc, obj, msg):
    try:
      data = json.loads(msg.payload)
      logger.info(data)
      
      # Execute Commands from Erika
      if "cmd" in data:
        if data["cmd"] == "email":
          subject = f'Erika Text {datetime.now().strftime("%d.%m.%Y")}'
          content = Textdata.as_fulltext(data['hashid'])
          return send_email(data['from'],data['to'],subject, content)

      try:
        Textdata.create(content=data['line'], hashid=data['hashid'], line_number=data['lnum'])
      except IntegrityError:
        logger.info("Already saved line {}".format(data['line']))
    except ValueError as e:
      logger.info(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
  
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

