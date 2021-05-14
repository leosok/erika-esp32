from bottle import route, run

import time
from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD
import json

import app.model
import app.mqqt


# Create/Open database
app.model.initialize_models()

app.mqqt.start_mqqt(MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD)


