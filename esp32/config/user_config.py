
from .configurator import Configurator

class UserConfig(Configurator):

    ERIKA_CLOUD_HOST = "https://www.erika-cloud.de"
    CONF_FILE = 'config/user_config.json'
    WELCOME_FILE = 'config/welcome.txt'

    
    def __init__(self):
        self.wlan_password = None
        self.wlan_ssid = None
        self.erika_name = None
        self.email_adress = None
        self.user_firstname = None
        self.user_lastname = None
        
        self.load()
        
    def save(self):
        """
        Saves UserConfig to json
        """
        with open(self.CONF_FILE, 'w') as f:
            json.dump(self.__dict__, f)


    def load_welcome_text(self):
        """
        Loads Welcome.txt
        Returns: text or False
        """
        try:
            with open(self.WELCOME_FILE, 'r') as f:
                return '\n'.join(f.readlines())
        except:
            return False

    def delete(self):
        """
        Delets config from JSON
        Returns: True or False (if config_file cannot be deleted)
        """
        import os
        try:
            os.remove(self.CONF_FILE)
            return True
        except:
            return False