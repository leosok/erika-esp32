import os
from utils.misc import capitalize

PLUGINS = []
PLUGIN_DIR = '/plugins'
exclued_files = ['__init__.py', 'erika_plugin_base.py']

files = [name[:-3] for name in os.listdir(PLUGIN_DIR)
            if name.endswith('.py') and name not in exclued_files]
for file in files:
    print(file)
    plugin_module =__import__(PLUGIN_DIR + '/' + file) # type: ignore
    plugin_class = getattr(plugin_module, capitalize(file) )
    plugin_class.cool("hallo")