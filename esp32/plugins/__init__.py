import os

# Contrived example of generating a module named as a string
full_module_name = "mypackage." + "mymodule"

# The file gets executed upon import, as expected.

PLUGINS = []
PLUGIN_DIR = '/plugins'
exclued_files = ['__init__.py', 'erika_plugin_base.py']

def capitalize(string:str) -> str:
    return string[0].upper() + string[1:]


files = [name[:-3] for name in os.listdir(PLUGIN_DIR)
            if name.endswith('.py') and name not in exclued_files]
for file in files:
    print(file)
    plugin_module =__import__(PLUGIN_DIR + '/' + file)
    plugin_class = getattr(plugin_module, capitalize(file) )
    plugin_class.cool("hallo")