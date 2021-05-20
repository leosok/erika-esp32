from bottle import route, run, hook, view, default_app, request, redirect
import time
import json
import logging
from app.model import db, initialize_models, Textdata

logging.basicConfig()
logger = logging.getLogger('erika_bottle')
logger.setLevel(logging.DEBUG)

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
        

@route('/pages')
@view('all_pages.tpl.html')
def all():
    pages = Textdata.select().order_by(Textdata.timestamp.asc()).group_by(Textdata.hashid)
    return dict(pages=pages)

@route('/pages/<hashid>')
@view('single_page.tpl.html')
def single(hashid):
    if request.query.action == "delete":
        logger.info(f"Deleting {hashid}")
        Textdata.delete().where(Textdata.hashid==hashid).execute()
        redirect("/pages")
    else:
        lines = Textdata.select().where(Textdata.hashid==hashid).order_by(Textdata.line_number)
        return dict(lines=lines, fulltext=Textdata.as_fulltext(hashid))


@route('/incoming', method='POST')
def incoming_webhook():
    
    from app.mqqt import ErikaMqqt
    from secrets import MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD
    erika_mqqt = ErikaMqqt(MQQT_SERVER, MQQT_USERNAME, MQQT_PASSWORD)

    # Create a german date to print
    import locale
    from email.utils import parsedate_to_datetime
    mail_date = parsedate_to_datetime(request.json['headers']['date'])
    locale.setlocale(locale.LC_TIME, "de_DE")
    print_date = mail_date.strftime("%A, %d %b %Y %H:%M")


    print_template = [
        "\n\n",
        "--------  EMAIL -------\n",
        "{}".format(print_date),
        "Von: {}".format(request.json['headers']['from']),
        "Btr.: {}".format(request.json['headers']['subject']),
        " ",
        "{}".format(request.json['plain'])        
    ]

    print_str = '\n'.join(print_template)
    erika_mqqt.mqttc.publish('erika/1/print',print_str)
    
    return "ok"


initialize_models()
db.close()
application = default_app()

if __name__ == "__main__":
    run(host='localhost', port=8080, debug=True, reloader=True)