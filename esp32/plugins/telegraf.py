from mqtt_connection import ErikaMqqt
from plugins.erika_plugin_base import ErikaBasePlugin

class Telegraf(ErikaBasePlugin):
    def __init__(self, erika:Erika=None, erika_mqqt:ErikaMqqt=None): # type: ignore
        
        super().__init__(
            erika=erika, 
            erika_mqqt=erika_mqqt
            )
    def on_message(self, topic: str, msg: str):
        return super().on_message(topic, "Telegraf received: "+msg)