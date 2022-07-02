import time


class Debuglogger:
    """
    A class to help to messure how long stuff takes.
    Use like:
    
    deb = Debuglogger()
    deb.start("Foo")
    foo()
    deb.done()
    """

    def __init__(self, module=None):
        self.t_start = time.ticks_ms()
        self.last_tick = None
        self.last_text = None
        if module:
            self.module = f"[{module}]"
        else:
            self.module = ""

    def start(self, text: str):
        self.last_tick = time.ticks_ms()
        self.last_text = text
        print("{total:4d}ms [start]{module} {txt}".format(
            txt=text, total=time.ticks_ms(), module=self.module))

    def done(self):
        print("{total:4d}ms [done]{module}  {txt}, diff: {diff}ms ".format(
            txt=self.last_text,
            diff=time.ticks_diff(time.ticks_ms(), self.last_tick),
            total=time.ticks_ms(),
            module=self.module))
