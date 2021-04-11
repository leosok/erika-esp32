
# Based on https://bradgignac.com/2014/05/12/sending-email-with-python-and-the-mailgun-api.html

import urequests as requests
from secrets import MAILGUN_API_KEY, CONFIG_MY_EMAIL
import binascii
import os
from boot import do_connect


def encode_multipart_formdata(fields):
    '''
    Encoding algorithm from
    https://julien.danjou.info/handling-multipart-form-data-python/
    '''
    boundary = binascii.hexlify(os.urandom(16)).decode('ascii')

    body = (
        "".join("--%s\r\n"
                "Content-Disposition: form-data; name=\"%s\"\r\n"
                "\r\n"
                "%s\r\n" % (boundary, field, value)
                for field, value in fields.items()) +
        "--%s--\r\n" % boundary
    )

    content_type = "multipart/form-data; boundary=%s" % boundary

    return body, content_type


def send_mailgun(mail_text, mail_from="erika@news.belavo.co", mail_to=CONFIG_MY_EMAIL, mail_subject="Erika Transcript"):

    headers = {}
    auth_str = b"api:{}".format(MAILGUN_API_KEY)
    # transcoding adds a \n character, we need to remove
    auth_base = binascii.b2a_base64(auth_str).strip()
    headers["Authorization"] = b"Basic " + auth_base
    #headers["Authorization"] = "Basic YXBpOmJkYmRjYjg0M2EzZGZiYzI1YzQ4Y2Q4OTIwZjY1YTUxLTM5MzliOTNhLWQ5NWU2NWUz"

    ajson = {
        "from": mail_from,
        "to": mail_to,
        "subject": mail_subject,
        "text": mail_text}

    data, content_type = encode_multipart_formdata(ajson)
    headers["Content-Type"] = content_type
  
    # This is nesseccary for the request to finish, when data transmission is done - 
    # if not set urequests lingers around for another 10 seconds blocking everything
    headers["Connection"] = 'Close'

    r = requests.post(url="https://api.mailgun.net/v3/news.belavo.co/messages",
                      headers=headers,
                      data=data)

    print(r.text)
