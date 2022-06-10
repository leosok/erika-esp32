from mqtt_connection import ErikaMqqt
from plugins.erika_plugin_base import ErikaBasePlugin
import json

class Telegraf(ErikaBasePlugin):
    def __init__(self, erika:Erika=None, erika_mqqt:ErikaMqqt=None): # type: ignore
        
        super().__init__(
            erika=erika, 
            erika_mqqt=erika_mqqt,
            keylogging=True,
            #active=True
            )
    def on_message(self, topic: str, msg: str):
        return super().on_message(topic, "Telegraf received: "+msg)

    async def on_keystroke(self, key=""):
        erika_mqqt = self.erika_mqqt
        data={"sender": self.erika.uuid, "text":key}
        await erika_mqqt.client.publish(erika_mqqt.channel_print_all, json.dumps(data), qos=0)
        return