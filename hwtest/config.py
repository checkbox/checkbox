import re
import os

from ConfigParser import ConfigParser


class IncludeDict(dict):

    def __init__(self, parser):
        super(IncludeDict, self).__init__()
        self._parser = parser

    def __setitem__(self, key, value):
        if key == "includes":
            for path in re.split(r"\s+", value):
                if not os.path.exists(path):
                    raise Exception, "No such configuration file: %s" % path
                self._parser.read(path)

        super(IncludeDict, self).__setitem__(key, value)


class ConfigSection(object):

    def __init__(self, parent, name, **kwargs):
        self.parent = parent
        self.name = name
        self._kwargs = kwargs

    def _get_value(self, attr):
        return self._kwargs.get(attr)

    def __getattr__(self, attr):
        if attr in self._kwargs:
            return self._get_value(attr)

        raise AttributeError, attr


class ConfigDefaults(ConfigSection):

    def _get_value(self, attr):
        return os.environ.get(attr.upper()) \
            or os.environ.get(attr.lower()) \
            or super(ConfigDefaults, self)._get_value(attr)

    def __getattr__(self, attr):
        if attr in self._kwargs:
            return self._get_value(attr)

        raise AttributeError, attr


class Config(object):

    def __init__(self, path):
        self.path = path
        self.sections = {}

        self._parser = ConfigParser()
        self._parser._defaults = IncludeDict(self._parser)

        if not os.path.exists(path):
            raise Exception, "No such configuration file: %s" % path
        self._parser.read(path)

    def get_defaults(self):
        kwargs = self._parser.defaults()
        return ConfigDefaults(self, 'DEFAULT', **kwargs)

    def get_section(self, section_name):
        if section_name in self._parser.sections():
            kwargs = dict(self._parser.items(section_name))
            return ConfigSection(self, section_name, **kwargs)

        return None

    def get_section_names(self):
        return self._parser.sections()
