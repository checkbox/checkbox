import os

from hwtest.lib.conversion import string_to_int


class Memory(object):

    default_filename = os.path.join(os.sep, 'proc', 'meminfo')

    def __init__(self, filename=None):
        self._filename = filename or self.default_filename

    @property
    def properties(self):
        meminfo = {}
        fd = file(self._filename, "r")

        for line in map(lambda l: l.strip(), fd.readlines()):
            if line.find(":") != -1:
                (key, value) = line.split(':', 1)
                key = key.strip()
                key = key.replace(' ', '_')
                value = value.strip()
                meminfo[key] = string_to_int(value)

        return meminfo
