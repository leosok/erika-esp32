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

    def delete(self):
        """
        Delets config from JSON
        Returns: True or False (if config_file cannot be deleted)
        """
        try:
            os.remove(self.CONF_FILE)
            return True
        except:
            return False

    

    async def get_config_io(self, erika:Erika):
        from utils.screen_utils import write_to_screen, show_progress, reset
        
        reset().show()
        erika.sender.alarm()        
        write_to_screen("Papier einlegen", line=3, centered=True)
        write_to_screen(" und ENTER", line=4, centered=True)    
        await erika.ask(" ") # just wait for the Enter

        reset().show()
        write_to_screen("Konfiguration", line=2, centered=True)
        show_progress(0,5)

        self.erika_name = await erika.ask("Wie heißt deine Erika?")
        show_progress(1,5)
        self.email_adress = await erika.ask("Deine Email-Adresse? - Nutze (at)")
        show_progress(2,5)
        
        # Wlan
        await erika.print_text("--- Wlan Configuration ---")
        await erika.print_text("Verfügbare Netzwerke:")

        wlans = scan_wlan()
        max_ssid_length = max([len(wlan[0]) for wlan in wlans])
        
        for idx, wlan in enumerate(wlans, start=1):
            print("->" + str(wlan))
            ssid, strength = wlan
            ssid_str = "{0:{1}s}".format(ssid, max_ssid_length+4)
            wlan_strength_str = get_wlan_strength(strength) * ")"
            wlan_line = "{}: {} {:4s}".format(idx, ssid_str, wlan_strength_str )
            await erika.print_text(wlan_line)
            print( wlan_line)

        erika.sender._newline
        wlan_number_str = await erika.ask("Bitte Nummer des Netwerks eingeben")
        show_progress(3,5)
        try:
            self.wlan_ssid = wlans[int(wlan_number_str)-1][0] # last 0 is for the tuple
        except IndexError:
            wlan_number_str = await erika.ask("'{}' ungültig. Bitte Nummer des Netwerks eingeben".format(wlan_number_str))
            self.wlan_ssid = wlans[int(wlan_number_str)-1][0] # last 0 is for the tuple

        self.wlan_password = await erika.ask("Bitte Passwort eingeben:")
        show_progress(3,5)

        if do_connect(self.wlan_ssid, self.wlan_password, timeout_sec=10):
            await erika.print_text("Verbindung mit '{}' hergestellt!".format(self.wlan_ssid))
            self.save()
            show_progress(5,5)
        else:
            await erika.print_text("Verbindungsfehler - Keine Verbindung mit '{}'.".format(self.wlan_ssid))
            self.wlan_password = await erika.ask("Bitte Passwort wiederholen")
            if do_connect(self.wlan_ssid, self.wlan_password, timeout_sec=10):
                await erika.print_text("Verbindung mit '{}' hergestellt!".format(self.wlan_ssid))
                self.save()

        show_progress(5,5)
        erika.sender._newline()
        await erika.print_text("Fertig! Starte neu, um Konfiguration zu laden.")
        from machine import reset
        reset()