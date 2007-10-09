import os
import re
import sys
import logging

from hwtest.log import format_object


class PluginManager(object):

    def __init__(self, reactor, config, persist, persist_filename=None):
        self.reactor = reactor
        self._config = config
        self._error = None

        # Load persistence
        self.persist = persist
        self._persist_filename = persist_filename
        if persist_filename and os.path.exists(persist_filename):
            self.persist.load(persist_filename)

        # Register plugins
        plugin_sections = self._config.get_defaults().plugins
        for section_name in re.split(r"\s+", plugin_sections):
            self.load_section(section_name)

    def load_section(self, name):
        logging.info("Loading plugin section %s", name)
        config = self._config.get_section(name)
        section = PluginSection(name, config)
        for plugin_name in section.get_plugin_names():
            self.load_plugin(section, plugin_name)

    def load_plugin(self, section, name):
        logging.info("Loading plugin %s from section %s",
            name, section.name)
        module = section.get_plugin_module(name)
        config_name = "/".join([section.name, name])
        config = self._config.get_section(config_name)
        plugin = module.factory(config)
        plugin.register(self)

    def flush(self):
        self.reactor.fire("flush")
        self._save_persist()

    def _save_persist(self):
        if self._persist_filename:
            self.persist.save(self._persist_filename)

    def set_error(self, error=None):
        self._error = error

    def get_error(self):
        return self._error


class PluginSection(object):

    def __init__(self, name, config):
        self.name = name
        self._config = config

    @property
    def directory(self):
        return os.path.expanduser(self._config.directory)

    def get_plugin_names(self):
        whitelist = re.split(r"\s+", self._config.whitelist or '')
        blacklist = re.split(r"\s+", self._config.blacklist or '')
        plugin_names = list(set(whitelist).difference(set(blacklist)))
        return plugin_names

    def get_plugin_modules(self):
        plugin_modules = []
        for plugin_name in self.get_plugin_names():
            plugin_module = self.get_plugin_module(plugin_name)
            plugin_modules.append(plugin_module)
    
        return plugin_modules

    def get_plugin_module(self, name):
        sys.path.insert(0, self.directory)
        module = __import__(name)
        del sys.path[0]

        if not hasattr(module, "factory"):
            raise Exception, "Factory variable not found: %s" % module

        return module
 

class Plugin(object):

    priority = 0
    persist_name = None

    def __init__(self, config):
        self.config = config

    def register(self, manager):
        self._manager = manager
        if hasattr(self, "run"):
            manager.reactor.call_on("run", self.run, self.priority)
        if self.persist_name is not None:
            self._persist = manager.persist.root_at(self.persist_name)
