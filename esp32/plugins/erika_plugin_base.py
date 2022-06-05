# Baseclass for Erika Plugins
from erika import Erika
from mqtt_connection import ErikaMqqt

class ErikaBasePlugin:
    """
    A Base Plugin Class. Use as Baseclass for you Plugins to get basic functionality.
    """
    def __init__(self, plugin_name:str="new_plugin", erika:Erika=None, mqqt:ErikaMqqt=None):
        self.erika=erika
        self.plugin_name = plugin_name
        self.__register_plugin()

    def __register_plugin(self):
        self.mqqt.plugins.append(self)

    def on_message(self, topic:str, msg:str):
        print(topic, msg)

    def send_message(self, topic:str, msg:str):
        print("sending {msg} to {topic}".format(msg=msg, topic=topic))
