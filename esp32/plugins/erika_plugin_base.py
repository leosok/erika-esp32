# Baseclass for Erika Plugins
from erika import Erika
from mqtt_connection import ErikaMqqt


class ErikaBasePlugin:
    """
    A Base Plugin Class. Use as Baseclass for you Plugins to get basic functionality.
    """

    info = "Ein Telegraf, der an alle Erikas sendet, die gerade an sind. ON/OFF"

    def __init__(self, erika: Erika = None, erika_mqqt: ErikaMqqt = None, topic=None, keylogging=False, active:bool=False):
        self._active = active
        self.erika = erika
        self.erika_mqqt = erika_mqqt
        self.plugin_name = self.__class__.__name__.lower()
        self.topic = topic or self.plugin_name
        self.keylogging = keylogging
        self.register_plugin()
        self.active = active

    def __repr__(self):
        return "<{} active: {} topic: {} keylogging {}".format(self.plugin_name, 
        self.active, self.topic, self.keylogging)

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, active):
        self._active = active
        if active:
            print("Plugin '{}' is ON".format(self.plugin_name))
            self.erika_mqqt.plugins.append(self)
            print(self.erika_mqqt.plugins)
        else:
            # turn off plugin
            print("Plugin '{}' is OFF".format(self.plugin_name))
            try:
                self.erika_mqqt.plugins.remove(self)
            except ValueError: # type: ignore
                pass

    async def activate(self, active:bool):
        """
        A fuction to be called by a foreign class, to set the active-setter
        """
        self.active = active     
        if self.topic:
            if self.erika_mqqt.client:
                if active:
                    # means mqqt client is fully loaded.
                    topic = self.erika_mqqt.__get_channel_name(self.topic)
                    print("subscribing to '{}'".format(topic))
                    await self.erika_mqqt.client.subscribe(topic=topic, qos=0)

    def register_plugin(self):
        """
        Will add the Plugin to the "docs" and to erika_mqqt.plugins
        Whenever a plugin is in the plugin folder, it will be mentioned in the docs
        """
        self.erika.action_controller.docs.update({self.plugin_name: ErikaBasePlugin.info})
        setattr(self.erika.action_controller, self.plugin_name, self.activate)
       
    def on_message(self, topic: str, msg: str):
        if self.active:
            print(topic, msg)

    def on_keystroke(self, key=""):
        if self.active:
            print("Plugin-Debug: '{}' Key (plugin: {}. Please overload this function.".format(key, self.plugin_name))
        
    def send_message(self, topic: str, msg: str):
        if self.active:
            print("sending {msg} to {topic}".format(msg=msg, topic=topic))
