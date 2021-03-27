#
# This is a picoweb example showing a web page route
# specification using view decorators (Flask style).
#
import picoweb
import machine
from erika import Erika
import ulogging as logging
from screen_utils import write_to_screen
from urllib import unquote

app = picoweb.WebApp(__name__)
erika = Erika()


def check_erika(timer):
  if erika.connection.any():
    print('Erika lives')
    ans = erika.connection.read()
    write_to_screen('Leben')
    

timer = machine.Timer(1)
timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=check_erika)

@app.route("/")
def index(req, resp):
    yield from picoweb.start_response(resp)
    yield from resp.awrite("Willst du <a href='print'> Hallo Welt?</a>.")

@app.route("/print")
def squares(req, resp):
    yield from picoweb.start_response(resp)
    if len(req.qs):
      str = unquote(req.qs)
    else:
      str= "Hallo Welt"
      
    erika.print_string(str + '\n')
    yield from resp.awrite("Printing <a href='print'> I want More!</a>.")
   


@app.route("/screen")
def screen_answ(req, resp):
    str = unquote(req.qs)
    write_to_screen(str)
    yield from picoweb.start_response(resp)
    yield from resp.awrite(str)
   
   
def start_server(ip):
  logging.basicConfig(level=logging.INFO)
  app.run(debug=True, host=ip, port=80)


