from mqtt_connection import ErikaMqqt
from plugins.erika_plugin_base import ErikaBasePlugin

class Telegraf(ErikaBasePlugin):
    def __init__(self, erika:Erika=None, mqqt:ErikaMqqt=None):
        super().__init__(
            plugin_name=self.__name__, 
            erika=erika, 
            mqqt=mqqt
            )
    def on_message(self, topic: str, msg: str):
        return super().on_message(topic, "knaller: "+msg)

    def cool(string):
        print("COOL: "+string)