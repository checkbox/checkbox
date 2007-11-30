import os
import re
import sys
import logging


class RepositorySection(object):
    """
    Repository section which is essentially a container of entries. These
    map to the modules referenced in the configuration passed as argument
    to the constructor.
    """

    def __init__(self, config, name):
        """
        Constructor which takes a configuration instance and name as
        argument. The former is expected to contain a directory and
        blacklist.
        """
        self._config = config
        self.name = name
        self._names = None
        self._entries = {}

    @property
    def directory(self):
        """
        Directory contained for this sections.
        """
        return os.path.expanduser(self._config.directory)

    def get_names(self):
        """
        Get all the module names contained in the directory for this
        section.
        """
        if self._names is None:
            directory_names = [p.replace('.py', '')
                for p in os.listdir(self.directory)
                if p.endswith('.py') and p != "__init__.py"]
            blacklist_names = re.split(r"\s+", self._config.blacklist or '')
            self._names = list(set(directory_names).difference(set(blacklist_names)))

        return self._names

    def load_all(self):
        """
        Load all modules contained in this section.
        """
        for name in self.get_names():
            self.load_entry(name)

        return self._entries.values()

    def has_entry(self, name):
        """
        Check if the given name is in this section.
        """
        return name in self.get_names()

    def load_entry(self, name):
        """
        Load a single moduble by name from this section.
        """
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
    """
    Repository manager which is essentially a container of sections.
    """

    _section_factory = RepositorySection

    def __init__(self, config):
        """
        Constructor which takes a configuration instance as argument. This
        will be used to load sections by name.
        """
        self._config = config
        self._error = None
        self._sections = {}

    def load_section(self, name):
        """
        Load a section by name which must correspond to an entry in the
        configuration instance pased as argument to the constructor.
        """
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
    """
    Repository base class which should be inherited by each repository
    implementation.
    """

    def __init__(self, config):
        """
        Constructor which takes a configuration instance as argument. This
        can be used to pass options to repositories.
        """
        self.config = config
