from bottle import route, run, hook, view, default_app, request, redirect, HTTPResponse, static_file
import time
import json
import logging
from app.model import db, initialize_models, Textdata, Typewriter, Message
from email.utils import parseaddr
from playhouse.shortcuts import model_to_dict
import os.path as op

logging.basicConfig()
logger = logging.getLogger('erika_bottle')
logger.setLevel(logging.DEBUG)
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



@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root=op.join(op.dirname(__file__), 'static'))

@route('/pages')
@view('all_pages.tpl.html')
def all():
    pages = Textdata.select().order_by(Textdata.timestamp.asc()).group_by(Textdata.hashid)
    return dict(pages=pages)

@route('/erika/<uuid>/emails')
@view('erika_single.tpl.html')
def erika_single(uuid):
    typewriter = Typewriter.select().where(Typewriter.uuid == uuid).get()
    emails = typewriter.messages.dicts()

    return dict(emails=emails)



@route('/pages/<hashid>')
@view('single_page.tpl.html')
def single(hashid):
    if request.query.action == "delete":
        logger.info(f"Deleting {hashid}")
        Textdata.delete().where(Textdata.hashid == hashid).execute()
        redirect("/pages")
    else:
        lines = Textdata.select().where(Textdata.hashid == hashid).order_by(Textdata.line_number)
        return dict(lines=lines, fulltext=Textdata.as_fulltext(hashid))


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

    typewriter = Typewriter.create(
        user_firstname = data['firstname'],
        user_lastname = data['lastname'],
        erika_name = data['erika_name'],
        user_email = data['email'].lower(),
        uuid = data['uuid'],
        email = f"{data['erika_name'].lower()}@{APP_HOST}",
        chat_active = data['chat_active']
    )

    print(f"Created Typewriter: {typewriter}")
    return "ok"


initialize_models()
db.close()
application = default_app()

if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)
