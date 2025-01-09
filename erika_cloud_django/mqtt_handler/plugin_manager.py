import importlib
import os
import logging
from typing import Dict, Type
from .plugins.base import MQTTPlugin

logger = logging.getLogger('mqtt_plugin_manager')

class PluginManager:
    def __init__(self, plugin_dir: str):
        self.plugin_dir = plugin_dir
        self.plugins: Dict[str, MQTTPlugin] = {}
        self.load_plugins()

    def load_plugins(self):
        """Load all plugins from the plugins directory"""
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                try:
                    module = importlib.import_module(f".plugins.{module_name}", package="mqtt_handler")
                    plugin_class = getattr(module, f"{module_name.title()}Plugin")
                    plugin = plugin_class()
                    self.plugins[plugin.command] = plugin
                    logger.info(f"Loaded plugin: {plugin}")
                except Exception as e:
                    logger.error(f"Failed to load plugin {module_name}: {e}")

    def handle_message(self, command: str, typewriter_id: str, payload: dict) -> bool:
        """Route message to appropriate plugin"""
        if command in self.plugins:
            try:
                return self.plugins[command].handle_message(typewriter_id, payload)
            except Exception as e:
                logger.error(f"Plugin {command} failed to handle message: {e}")
                return False
        logger.warning(f"No plugin found for command: {command}")
        return False
