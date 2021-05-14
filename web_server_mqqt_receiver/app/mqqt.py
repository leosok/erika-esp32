def on_message(mqttc, obj, msg):

  try:
    data = json.loads(msg.payload.decode())
    if data['doc']:
      print(data['line'])
  except ValueError as e:
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
 
  return True
    

# def on_publish(mqttc, obj, mid):
#     print("mid: " + str(mid))
# def on_subscribe(mqttc, obj, mid, granted_qos):
#     print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


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
mqttc.username_pw_set(MQQT_USERNAME, password=None)
mqttc.connect(MQQT_SERVER, 1883, 60)
mqttc.subscribe("erika/1/print", 0)

mqttc.loop_forever()
