# Based on https://bradgignac.com/2014/05/12/sending-email-with-python-and-the-mailgun-api.html
# pylint: disable=all

import binascii
import gc
import json
from secrets import CONFIG_MY_EMAIL, MAILGUN_API_KEY, MAILGUN_API_URL
import urequests as requests
from utils.timeit import time_acc_function
from utils.urlencode import urlencode


class Mailgun:

    def __init__(self, api_key, api_url):
        self.api_key = api_key
        self.api_url = api_url


    def post_formdata(self, url, data=None, json=None, headers=None):
        # This function works well, as long as the data is small (<5kb). Above this urlencode fails
        # on my esp32 because of memory fragmentation. A possible solution could be to use chunked 
        # posting (async?) using urlencode chunk by chunk, avoiding 
        
        if isinstance(data, dict):
            headers = {} if headers is None else headers
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
        gc.collect()
        return requests.post(url, data=urlencode(data), json=json, headers=headers)

    @time_acc_function
    def send_mailgun(self, mail_text, mail_from, mail_to, mail_subject):

        headers = {} 
        auth_str = b"api:{}".format(MAILGUN_API_KEY)
        
        # transcoding adds a \n character, we need to remove it
        auth_base = binascii.b2a_base64(auth_str).strip()
        headers["Authorization"] = b"Basic " + auth_base
    
        ajson = {
                "from": mail_from,
                "to": mail_to,
                "subject":mail_subject,
                "text": mail_text}

        response =  post_formdata(
            api_url,
            headers=headers,
            data=ajson)
        
        print(response.text)
        return response

