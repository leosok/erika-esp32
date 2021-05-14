from bottle import route, run, hook, view
import time
import json

from app.model import db, initialize_models, Textdata



@hook('before_request')
def _connect_db():
    db.connect()

@hook('after_request')
def _close_db():
    if not db.is_closed():
        db.close()
        

@route('/pages/')
@view('all_pages.tpl.html')
def all():
    pages = Textdata.select().group_by(Textdata.hashid)
    return dict(pages=pages)

@route('/pages/<hashid>')
@view('single_page.tpl.html')
def single(hashid):
    lines = Textdata.select().where(Textdata.hashid==hashid)
    return dict(lines=lines)

initialize_models()
db.close()
run(host='localhost', port=8080, debug=True, reloader=True)