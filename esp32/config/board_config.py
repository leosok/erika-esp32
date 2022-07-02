import ujson as json


class BoardConfig:
    """
    Loads config from JSON (which is not)
    Returns: dict or False (if config_file cannot be opend)
    """

    CONF_FILE = 'config/board_config.json'

    def __init__(self):
        self.erika_rts = None
        self.erika_cts = None
        self.erika_rx = None
        self.erika_tx = None

        self.screen_display_type = None
        self.screen_rst = None
        self.screen_scl = None
        self.screen_sda = None

        self.load()

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
        except:
            return False

    def __repr__(self):
        return str(self.__dict__)
