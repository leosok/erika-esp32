import os
import json
from erika import Erika
from utils.network_utils import scan_wlan, get_wlan_strength, do_connect



class MqqtConfig:

    CONF_FILE = 'config/mqqt_config.json'

    def __init__(self):
        self.MQQT_SERVER = None
        self.MQQT_USERNAME = None
        self.MQQT_PASSWORD = None
        
        self.load()

    def load(self):
        """
        Loads config from JSON
        Returns: dict or False (if config_file cannot be opend)
        """
        try:
            with open(self.CONF_FILE, 'r') as f:
                data = json.load(f)
            for k,v in data.items():
                setattr(self,k,v)
        except:
            return False

    def __repr__(self):
        return self.__dict__

class UserConfig:
    
    CONF_FILE = 'config/user_config.json'
    
    def __init__(self):
        self.wlan_password = None
        self.wlan_ssid = None
        self.erika_name = None
        self.email_adress = None
        
        self.load()

    def __repr__(self):
        return self.__dict__
        
    def save(self):
        """
        Saves UserConfig to json
        """
        with open(self.CONF_FILE, 'w') as f:
            json.dump(self.__dict__, f)

    def load(self):
        """
        Loads config from JSON
        Returns: dict or False (if config_file cannot be opend)
        """
        try:
            with open(self.CONF_FILE, 'r') as f:
                data = json.load(f)
            for k,v in data.items():
                setattr(self,k,v)
            return True
        except:
            return False


    

    async def get_config_io(self, erika:Erika):

        self.erika_name = await erika.ask("Wie heißt deine Erika?")
        self.email_adress = await erika.ask("Wie lautet deine Email-Adresse?")
        
        # Wlan
        await erika.print_text("--- Wlan Configuration ---")
        await erika.print_text("Verfügbare Netzwerke:")

        wlans = scan_wlan()
        
        for idx, wlan in enumerate(wlans, start=1):
            print("->" + str(wlan))
            ssid, strength = wlan
            await erika.print_text("{}: {:4s} {}".format(idx, get_wlan_strength(strength) * ")", ssid))
            print( "{}: {:3s} {}".format(idx, get_wlan_strength(strength) * ")", ssid))

        erika.sender._newline
        wlan_number_str = await erika.ask("Bitte Nummer des Netwerks eingeben")
        wlan_number_int = int(wlan_number_str)
        self.wlan_ssid = wlans[wlan_number_int-1][0] # last 0 is for the tuple
        self.wlan_password = await erika.ask("Bitte Passwort eingeben")
        # Try to connect for 5 sec
        if do_connect(self.wlan_ssid, self.wlan_password, timeout_sec=5):
            await erika.print_text("Verbindung mit '{}' hergestellt!".format(self.wlan_ssid))
            self.save()
        else:
            await erika.print_text("Verbindungsfehler - Konnte keine Verbindung mit '{}' herstellen.".format(self.wlan_ssid))
            self.wlan_password = await erika.ask("Bitte Passwort wiederholen")



#from config.configurator import Configurator
#ma = Configurator.UserConfig()