import os
from bottle import (route, run, hook, view, default_app,
                    request, redirect, HTTPResponse, static_file, auth_basic)
import time
import json
import logging
from app.model import db, initialize_models, Textdata, Typewriter, Message
from app.utils import is_date
from email.utils import parseaddr
from playhouse.shortcuts import model_to_dict
import os.path as op
from peewee import DoesNotExist
from dotenv import load_dotenv


logging.basicConfig()
logger = logging.getLogger('erika_bottle')
logger.setLevel(logging.DEBUG)
load_dotenv()
APP_HOST = 'erika-cloud.de'


@hook('before_request')
def strip_path():
    request.environ['PATH_INFO'] = request.environ['PATH_INFO'].rstrip('/')


@hook('before_request')
def _connect_db():
    db.connect()


@hook('after_request')
def _close_db():
    if not db.is_closed():
        db.close()


@route('/static/<filename:path>')
def send_static(filename):
    return static_file(filename, root=op.join(op.dirname(__file__), 'static'))


@route('/pages')
@view('all_pages.tpl.html')
def all():
    pages = Textdata.select().order_by(
        Textdata.timestamp.asc()).group_by(Textdata.hashid)
    return dict(pages=pages)


@route('/pages/<hashid>')
@view('single_page.tpl.html')
def single(hashid):
    if request.query.action == "delete":
        logger.info(f"Deleting {hashid}")
        Textdata.delete().where(Textdata.hashid == hashid).execute()
        redirect("/pages")
    else:
        lines = Textdata.select().where(
            Textdata.hashid == hashid).order_by(Textdata.line_number)
        return dict(lines=lines, fulltext=Textdata.as_fulltext(hashid))


@route('/erika/<uuid>/emails')
@view('erika_single.tpl.html')
def erika_single(uuid):
    typewriter = Typewriter.select().where(Typewriter.uuid == uuid).get()
    emails = typewriter.messages.dicts()

    return dict(emails=emails)


def check_pass(username, password):
    admin_pass = os.getenv("ADMIN_PWD")
    return username=="admin" and password==admin_pass


@route('/')
@view('main_page_sender.tpl.html')
def index_sender():
    typewriters = Typewriter.select().where(Typewriter.status == 1)
    # emails = typewriter.messages.dicts()
    print(typewriters)

    return dict(typewriters=typewriters)


@route('/erika/<erika_name>')
@view('erika_single.tpl.html')
def erika_sender(erika_name):
    #typewriter = Typewriter.select().where(Typewriter.erika_name == erika_name.lower())
    try:
        typewriter = Typewriter.select().where(
            Typewriter.erika_name == erika_name.lower()).get()
        print(f"{erika_name} : - : {typewriter.erika_name}")
        if typewriter.messages.count():
            return dict(emails=typewriter.messages.dicts())
        else:
            return HTTPResponse(status=404, body=f"No messages for typewriter `{erika_name.capitalize()}`")
    except DoesNotExist:
        return HTTPResponse(status=404, body=f"No typewriter found with name `{erika_name.capitalize()}`")


@route('/incoming', method='POST')
@route('/incoming_email', method='POST')
def incoming_webhook():
    data = request.json

    receiver_name, receiver_email = parseaddr(data['headers']['to'])
    sender_name, sender_email = parseaddr(data['headers']['from'])
    erika = Typewriter.select().where(Typewriter.email == receiver_email)
    if not erika:
        return HTTPResponse(status=404, body=f"No Typewriter found for adress {receiver_email}")

    msg = Message.create(
        typewriter=erika,
        sender=sender_email,
        subject=data['headers']['subject'],
        body=data['plain']
    )

    print(f"Created Message: {msg}")
    return "ok"


@route('/typewriter', method='POST')
def register_typewriter():
    data = request.json

    #ToDo if erika_mail is already taken

    typewriter = Typewriter.create(
        user_firstname=data.get('firstname',''),
        user_lastname=data.get('lastname',''),
        erika_name=data.get('erika_name','').lower(),
        user_email=data.get('email','').lower(),
        uuid=data.get('uuid'),
        email=f"{data.get('erika_name','').lower()}@{APP_HOST}",
        chat_active=data.get('chat_active','')
    )

    print(f"Created Typewriter: {typewriter}")
    response = {"erika_mail": typewriter.email}
    return json.dumps(response)


@route('/admin/typewriters', method='GET')
@auth_basic(check_pass)
@view('model_list.tpl.html')
def admin_typewriters():
    typewriters = Typewriter.select().dicts()
    try:
        if typewriters.count():
            logger.info(typewriters)
            return dict(models=typewriters, is_date=is_date)
        else:
            return HTTPResponse(status=404, body=f"No messages for typewriter `{erika_name.capitalize()}`")
    except DoesNotExist:
        return HTTPResponse(status=404, body=f"No typewriter found with name `{erika_name.capitalize()}`")


initialize_models()
db.close()
application = default_app()

if __name__ == "__main__":
    run(host='0.0.0.0', port=8080, debug=True, reloader=True)
