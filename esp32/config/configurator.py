import ujson as json

class Configurator:
    
    def load(self):
        """
        Loads config from JSON
        Returns: dict or False (if config_file cannot be opend)
        """
        try:
            with open(self.CONF_FILE, 'r') as f:
                data = json.load(f)
            for k, v in data.items():
                setattr(self, k, v)
            return True
        except:
            return False

    def __repr__(self):
        return str(self.__dict__)
