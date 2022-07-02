from .configurator import Configurator

class BoardConfig(Configurator):
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
