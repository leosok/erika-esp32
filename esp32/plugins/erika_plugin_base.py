# Baseclass for Erika Plugins
from erika import Erika
from mqtt_connection import ErikaMqqt


class ErikaBasePlugin:
    """
    A Base Plugin Class. Use as Baseclass for you Plugins to get basic functionality.
    """

    def __init__(self, erika: Erika = None, erika_mqqt: ErikaMqqt = None, topic=None, keylogging=False):
        self.erika = erika
        self.erika_mqqt = erika_mqqt
        self.plugin_name = self.__class__.__name__.lower()
        self.topic = topic or self.plugin_name
        self.keylogging = keylogging
        self.__register_plugin()

    def __register_plugin(self):
        self.erika_mqqt.plugins.append(self)

    def on_message(self, topic: str, msg: str):
        print(topic, msg)

    def on_keystroke(self, key=""):
        print("'{}'-Key (plugin: {}".format(key, self.plugin_name))
        pass

    def send_message(self, topic: str, msg: str):
        print("sending {msg} to {topic}".format(msg=msg, topic=topic))
