
# Based on https://bradgignac.com/2014/05/12/sending-email-with-python-and-the-mailgun-api.html

import json
import urequests as requests
from utils.urlencode import urlencode
from secrets import MAILGUN_API_KEY, CONFIG_MY_EMAIL
import binascii


def post_formdata(url, data=None, json=None, headers=None):
    if isinstance(data, dict):
        data = urlencode(data)
        print(data)
        headers = {} if headers is None else headers
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    return requests.post(url, data=data, json=json, headers=headers)



def send_mailgun(mail_text, mail_from= "erika@news.belavo.co",mail_to=CONFIG_MY_EMAIL, mail_subject="Erika Transcript"):

    headers = {} 
    auth_str = b"api:{}".format(MAILGUN_API_KEY)
    # transcoding adds a \n character, we need to remove
    auth_base = binascii.b2a_base64(auth_str).strip()
    headers["Authorization"] = b"Basic " + auth_base
    #headers["Authorization"] = "Basic YXBpOmJkYmRjYjg0M2EzZGZiYzI1YzQ4Y2Q4OTIwZjY1YTUxLTM5MzliOTNhLWQ5NWU2NWUz"

    ajson = {
            "from": mail_from,
            "to": mail_to,
            "subject":mail_subject,
            "text": mail_text}
    
    print(ajson)

    r =  post_formdata(
        "https://api.mailgun.net/v3/news.belavo.co/messages",
        headers=headers,
        data=ajson)
    
    print(r.text)