from bottle import route, run

import time
from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD
import json

import app.model
import app.mqqt


@route('/hello')
def hello():
    return "Hello World!" 

app.mqqt.start_mqqt(MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD)

#run(host='localhost', port=8080, debug=True)

