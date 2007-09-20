import os
import sys
import logging

from hwtest.log import format_object


class PluginManager(object):
    def __init__(self, reactor, report, persist, persist_filename=None):
        self.reactor = reactor
        self.report = report
        self._plugins = []
        self._error = None

        self.persist = persist
        self._persist_filename = persist_filename
        if persist_filename and os.path.exists(persist_filename):
            self.persist.load(persist_filename)

    def load(self, directory):
        logging.info("Loading plugins from %s.", directory)
        sys.path.insert(0, directory)
        for name in [file for file in os.listdir(directory)
                     if file.endswith(".py")]:
            module_name = name.rstrip('.py')
            module = __import__(module_name)
            self.add(module.factory())
        del sys.path[0]

    def add(self, plugin):
        logging.info("Registering plugin %s.", format_object(plugin))
        self._plugins.append(plugin)
        plugin.register(self)

    def get_plugins(self):
        """Get the list of plugins."""
        return self._plugins

    def flush(self):
        self.reactor.fire("flush")
        self._save_persist()

    def exchange(self):
        self.flush()
        self.reactor.fire("exchange")
        self._save_persist()

    def _save_persist(self):
        if self._persist_filename:
            self.persist.save(self._persist_filename)

    def set_error(self, error=None):
        self._error = error

    def get_error(self):
        return self._error


class Plugin(object):
    pass
