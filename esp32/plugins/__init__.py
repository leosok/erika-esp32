#from erika.erika import Erika
#from mqtt_connection import ErikaMqqt
import os
from utils.misc import capitalize

PLUGINS = []
PLUGIN_DIR = '/plugins'
exclued_files = ['__init__.py', 'erika_plugin_base.py']

def register_plugins(erika:Erika=None, erika_mqqt:ErikaMqqt=None):
    files = [name[:-3] for name in os.listdir(PLUGIN_DIR)
                if name.endswith('.py') and name not in exclued_files]
    for file in files:
        plugin_module =__import__(PLUGIN_DIR + '/' + file) # type: ignore
        plugin_class = getattr(plugin_module, capitalize(file))
        plugin = plugin_class(erika=erika, erika_mqqt=erika_mqqt)
        plugin.register_plugin()