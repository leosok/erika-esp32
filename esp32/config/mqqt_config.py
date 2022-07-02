from .configurator import Configurator

class MqqtConfig(Configurator):

    CONF_FILE = 'config/mqqt_config.json'

    def __init__(self):
        self.MQQT_SERVER = None
        self.MQQT_USERNAME = None
        self.MQQT_PASSWORD = None
        
        self.load()
   