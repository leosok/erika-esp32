
#########################################
## A simple Pastebin Api class         ##
#########################################


from secrets import PASTEBIN_API_KEY, PASTEBIN_USER_API_KEY
import urequests
import time
from utils.urlencode import urlencode


def post_formdata(url, data=None, json=None, headers=None):
    if isinstance(data, dict):
        data = urlencode(data)
        headers = {} if headers is None else headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return urequests.post(url, data=data, json=json, headers=headers)


class Pastebin():

    def __init__(self):
        pass
    
    def paste(self, text, private=True):
        
        url = "https://pastebin.com/api/api_post.php"
        private_int = int(private) + 1 # 1=Unlisted, 2=Private
        date_str = ".".join([str(t) for t in time.localtime()[0:3]])
        paste_name = "Erika {}".format(date_str)

        data = {
            "api_dev_key" : PASTEBIN_API_KEY,
            "api_user_key" : PASTEBIN_USER_API_KEY,
            "api_paste_code" : text,
            "api_paste_private" : private_int,
            "api_option" : "paste",
            "api_paste_name" : paste_name
        }

        #post_data = ujson.dumps(data)

        resp = post_formdata(url, data=data)
        return resp.text