# utils for erika bottle utils

import logging
from dateutil.parser import parse

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        if ("-" in string) and ("." in string):
            # checking for "-" and "." so id's will not be matched
            date = parse(string, fuzzy=fuzzy)
            return date.strftime("%d.%m.%y %H:%M:%S")
        else:
            return False

    except ValueError:
        return False