
#########################################
## A simple PasteEE Api class         ##
#########################################
# Based on https://github.com/kartikjagdale/Pastee/


from secrets import PASTEE_API_KEY
import urequests
import time
from utils.urlencode import urlencode
import json


class Pastee():

    def __init__(self):
        pass

    def paste(self, text, desc='from Erika', private=True):

        date_str = "/".join([str(t) for t in time.localtime()[0:3]])
        desc = "Erika {}".format(date_str)

        url = 'https://api.paste.ee/v1/pastes'
        # Parameters to pass to the Pastee API
        sections = [{"name":"Section1","syntax":"autodetect","contents": text }]
        post_params = {#'key': PASTEE_API_KEY,
                       "description": desc,
                       "sections": sections
                       }

        json_params = json.dumps(post_params)
        print(json_params)

        # Post the params to Pastee API and get the url
        # try: 
        r = urequests.post(url, json=json_params, headers={
                        "X-Auth-Token": PASTEE_API_KEY})
        
        print(r.content)
        return r.content
        # except:
        #     print("Error requesting Paste.ee")

        
