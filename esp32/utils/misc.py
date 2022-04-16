from utils.timeit import timed_function
from erika import Erika

@timed_function
def file_lines_count(filename):
    with open(filename) as f:
        for i, l in enumerate(f):
            pass
    return i + 1

def status_led(status:bool, pin=25):
    """
    Activates a Status-LED on the Heltec-Board
    """
    from machine import Pin
    OnboardLED = Pin(pin, Pin.OUT)
    OnboardLED.value(status)