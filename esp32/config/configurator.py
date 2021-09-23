import os
import json

class Configurator:

    CONF_FILE = 'config/config.json'

    def __init__(self):
        pass

    def has_configuration():
        try:
            os.stat(Configurator.CONF_FILE)
            return True
        except:
            return False


    class UserConfig:
       
        def __init__(self):
            self.wlan_password = None
            self.wlan_ssid = None
            self.erika_name = None

        def __repr__(self):
            return self.__dict__
            
        def save(self):
            """
            Saves UserConfig to json
            """
            with open(Configurator.CONF_FILE, 'w') as f:
                json.dump(self.__dict__, f)

        def load(self):
            """
            Loads config from JSON
            Returns: dict
            """
            with open(Configurator.CONF_FILE, 'r') as f:
                data = json.load(f)
            for k,v in data.items():
                setattr(self,k,v)
            

#from config.configurator import Configurator
#ma = Configurator.UserConfig()