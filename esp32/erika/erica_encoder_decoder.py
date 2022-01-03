import json
from struct import *
from erika import char_map


def transpose_dict(dictionary):
    return {value: key for key, value in dictionary.items()}


class DDR_ASCII:
    def __init__(self, *args, **kwargs):
        """read conversion table from file and populate 2 dicts"""
        # with open(self.CONVERSION_TABLE_PATH, encoding="UTF-8") as f:
        self.ascii_2_ddr = char_map.A2E
        self.ddr_2_ascii = transpose_dict(self.ascii_2_ddr)
        self.ddr_2_page_controls = transpose_dict(char_map.page_controls)

    def byte_to_hex_str(self, bytes):
        # will return something like "0x4a"
        temp=unpack('B', bytes)[0]
        # will return something like "4A"
        return hex(temp)[2:4].upper()


    def encode(self, data):
        try:
            char = self.ascii_2_ddr[data]
        except KeyError:
            char = ''
        return char

    def try_encode(self, data, input_as_default=True):
        default = data if input_as_default else None
        return self.ascii_2_ddr.get(data, default)
    
    def decode(self, byte_data):

        return_char = self.ddr_2_ascii.get(byte_data) or self.ddr_2_page_controls.get(byte_data)
        if return_char is None:
            return_char=""
            print("Error decoding: {}".format(unpack('B', byte_data)[0]))

        return return_char

    def try_decode(self, data, input_as_default=True):
        default = data if input_as_default else None
        return self.ddr_2_ascii.get(data, "default")
