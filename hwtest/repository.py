import os
import re
import sys
import logging


class RepositorySection(object):

    def __init__(self, config, name):
        self._config = config
        self.name = name
        self._names = None
        self._entries = {}

    @property
    def directory(self):
        return os.path.expanduser(self._config.directory)

    def get_names(self):
        if self._names is None:
            directory_names = [p.replace('.py', '')
                for p in os.listdir(self.directory)
                if p.endswith('.py') and p != "__init__.py"]
            blacklist_names = re.split(r"\s+", self._config.blacklist or '')
            self._names = list(set(directory_names).difference(set(blacklist_names)))

        return self._names

    def load_all(self):
        for name in self.get_names():
            self.load_entry(name)

        return self._entries.values()

    def has_entry(self, name):
        return name in self.get_names()

    def load_entry(self, name):
        if name not in self._entries:
            logging.info("Loading name %s from section %s",
                name, self.name)

            sys.path.insert(0, self.directory)
            module = __import__(name)
            del sys.path[0]

            if not hasattr(module, "factory"):
                raise Exception, "Factory variable not found: %s" % module

            config_name = "/".join([self.name, name])
            config = self._config.parent.get_section(config_name)
            self._entries[name] = module.factory(config)

        return self._entries[name]


class RepositoryManager(object):

    _section_factory = RepositorySection

    def __init__(self, config):
        self._config = config
        self._error = None
        self._sections = {}

    def load_section(self, name):
        if name not in self._sections:
            logging.info("Loading repository section %s", name)
            config = self._config.get_section(name)
            self._sections[name] = self._section_factory(config, name)

        return self._sections[name]

    def set_error(self, error=None):
        self._error = error

    def get_error(self):
        return self._error


class Repository(object):

    def __init__(self, config):
        self.config = config
