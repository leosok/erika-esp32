from bottle import route, run
import paho.mqtt.client as mqtt
import time
from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD
import json






@route('/hello')
def hello():
    return "Hello World!" 

run(host='localhost', port=8080, debug=True)

