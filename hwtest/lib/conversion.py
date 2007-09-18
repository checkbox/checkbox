import re
import types


def string_to_int(string):
    conversion_table = {
        '(yes|true)': lambda v: True,
        '(no|false)': lambda v: False,
        '\d+.\d+': lambda v: float(v.group(0)),
        '(\d+)( b)?': lambda v: int(v.group(1)),
        '(\d+) kb': lambda v: int(v.group(1)) * 1024,
        '(\d+) mb': lambda v: int(v.group(1)) * 1024 * 1024,
        '(\d+) gb': lambda v: int(v.group(1)) * 1024 * 1024 * 1024,
        '(\d+)( hz)?': lambda v: int(v.group(1)),
        '(\d+) khz': lambda v: int(v.group(1)) * 1024,
        '(\d+) mhz': lambda v: int(v.group(1)) * 1024 * 1024,
        '(\d+) ghz': lambda v: int(v.group(1)) * 1024 * 1024 * 1024}

    for regex, func in conversion_table.items():
        match = re.match('^%s$' % regex, string, re.IGNORECASE)
        if match:
            return func(match)

    return string
