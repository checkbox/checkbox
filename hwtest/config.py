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
                self._parser.read(path)

        super(IncludeDict, self).__setitem__(key, value)


class ConfigSection(object):

    def __init__(self, name, parent, **kwargs):
        self.name = name
        self.parent = parent
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

    def __init__(self, config_parser=None):
        self.sections = {}

        self._parser = config_parser or ConfigParser()
        self._parser._defaults = IncludeDict(self._parser)

    def load_path(self, path):
        if not os.path.exists(path):
            raise Exception, "No such configuration file: %s" % path
        self._parser.read(path)

    def get_defaults(self):
        kwargs = self._parser.defaults()
        return ConfigDefaults('DEFAULT', self, **kwargs)

    def get_section(self, section):
        if section_name in self._parser.sections():
            kwargs = dict(self._parser.items(section_name))
            return ConfigSection(section_name, self, **kwargs)

        return None

    def get_section_names(self):
        return self._parser.sections()
