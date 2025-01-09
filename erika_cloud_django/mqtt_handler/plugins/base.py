from abc import ABC, abstractmethod
import logging

class MQTTPlugin(ABC):
    """Base class for MQTT message handling plugins"""
    
    def __init__(self):
        self.logger = logging.getLogger(f'mqtt_plugin.{self.__class__.__name__}')
        self.active = True

    @abstractmethod
    def handle_message(self, typewriter_id: str, payload: dict) -> bool:
        """Handle an incoming MQTT message"""
        pass

    @property
    def command(self) -> str:
        """The command this plugin handles"""
        return self.__class__.__name__.lower().replace('plugin', '')

    def __repr__(self):
        return f"<{self.__class__.__name__} active={self.active}>"
