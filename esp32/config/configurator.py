import os
import json
from erika import Erika
from utils.network_utils import scan_wlan, get_wlan_strength, do_connect
import uasyncio as asyncio
import urequests
import machine

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
        try:
            os.remove(self.CONF_FILE)
            return True
        except:
            return False

    

    async def get_config_io(self, erika:Erika):
        from utils.screen_utils import write_to_screen, show_progress, reset
        CONFIG_STEPS = 5

        reset().show()
        await erika.ask_for_paper()
        
        await erika.print_text(self.load_welcome_text())

        reset().show()
        write_to_screen("Konfiguration", line=2, centered=True)
        show_progress(0,CONFIG_STEPS)

        self.erika_name = await erika.ask("Wie heißt deine Erika?")
        show_progress(1,CONFIG_STEPS)
        self.user_firstname = await erika.ask("Dein Vorname")
        show_progress(2,CONFIG_STEPS)
        self.user_lastname = await erika.ask("Dein Nachname")
        show_progress(3,CONFIG_STEPS)
        self.email_adress = await erika.ask("Deine Email-Adresse? - Nutze (at)")
        self.email_adress = self.email_adress.replace('(at)', '@')
        show_progress(4,CONFIG_STEPS)
        
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

        erika.sender._newline()
        wlan_number_str = await erika.ask("Bitte Nummer des Netwerks eingeben")
        show_progress(5,CONFIG_STEPS)
        try:
            self.wlan_ssid = wlans[int(wlan_number_str)-1][0] # last 0 is for the tuple
        except IndexError:
            wlan_number_str = await erika.ask("'{}' ungültig. Bitte Nummer des Netwerks eingeben".format(wlan_number_str))
            self.wlan_ssid = wlans[int(wlan_number_str)-1][0] # last 0 is for the tuple

        self.wlan_password = await erika.ask("Bitte Passwort eingeben")
        show_progress(5,CONFIG_STEPS)

        if do_connect(self.wlan_ssid, self.wlan_password, timeout_sec=10):
            await erika.print_text("Ok: Verbindung mit '{}' hergestellt!".format(self.wlan_ssid))
            self.save()
            show_progress(5,CONFIG_STEPS)
        else:
            await erika.print_text("Verbindungsfehler - Keine Verbindung mit '{}'.".format(self.wlan_ssid))
            self.wlan_password = await erika.ask("Bitte Passwort wiederholen")
            if do_connect(self.wlan_ssid, self.wlan_password, timeout_sec=10):
                await erika.print_text("Ok: Verbindung mit '{}' hergestellt!".format(self.wlan_ssid))
                self.save()

        show_progress(6,CONFIG_STEPS)
        erika.sender._newline()
        
        typewriter_config = {
            "firstname" : self.user_firstname,
            "lastname": self.user_lastname,
            "erika_name" : self.erika_name,
            "uuid" : erika.uuid,
            "email" : self.email_adress,
            "chat_active" : True
            }
        
        resp = urequests.post(url=self.ERIKA_CLOUD_HOST + '/typewriter', json=typewriter_config)
        print("Server returned: {}".format(resp.status_code))
        erika_returned_mail = resp.json()['erika_mail']
        #todo: make chat un-optable
        await erika.print_text("Anmeldung an der Cloud erfolgreich.")
        await erika.print_text("Empfange Emails auf: {}".format(erika_returned_mail.replace('@','(at)')))
        await erika.print_text("Fertig! Starte neu, um Konfiguration zu laden.")
        #from machine import reset
        machine.reset()