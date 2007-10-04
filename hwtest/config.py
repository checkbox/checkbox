import os
from ConfigParser import ConfigParser


class ConfigSection(object):

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def _get_value(self, attr):
        return os.environ.get(attr.upper()) \
            or os.environ.get(attr.lower()) \
            or self._kwargs.get(attr.upper()) \
            or self._kwargs.get(attr.lower())

    def __getattr__(self, attr):
        if attr in self._kwargs:
            return self._get_value(attr)

        raise AttributeError, attr


class Config(object):

    def __init__(self, config_parser=None):
        self._parser = config_parser or ConfigParser()
        self.sections = {}

    def load_directory(self, directory):
        for name in [name for name in os.listdir(directory)
                     if name.endswith(".conf")]:
            self.load_path(os.path.join(directory, name))

    def load_path(self, path):
        self._parser.read(path)

    def get_section(self, section):
        if section in self._parser.sections():
            kwargs = dict(self._parser.items(section))
            return ConfigSection(**kwargs)

        return None

    def get_section_names(self):
        return self._parser.sections()
