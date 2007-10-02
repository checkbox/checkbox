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

    def load_directory(self, directory):
        logging.info("Loading plugins from directory: %s", directory)
        for name in [file for file in os.listdir(directory)
                     if file.endswith(".py")]:
            self.load_path(os.path.join(directory, name))

    def load_path(self, path):
        logging.info("Loading plugin from path: %s", path)
        directory = os.path.dirname(path)
        filename = os.path.basename(path)

        sys.path.insert(0, directory)
        name = filename.rstrip('.py')
        module = __import__(name)
        if not hasattr(module, "factory"):
            raise Exception, "Factory variable not found: %s" % module
        self.load(module.factory())

        del sys.path[0]

    def load(self, plugin):
        logging.info("Registering plugin: %s", format_object(plugin))
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

    run_priority = 0
    gather_priority = 0
    exchange_priority = 0

    persist_name = None

    def register(self, manager):
        self._manager = manager
        if hasattr(self, "run"):
            manager.reactor.call_on("run", self.run, self.run_priority)
        if hasattr(self, "gather"):
            manager.reactor.call_on("gather", self.gather, self.gather_priority)
        if hasattr(self, "exchange"):
            manager.reactor.call_on("exchange", self.exchange, self.exchange_priority)
        if self.persist_name is not None:
            self._persist = manager.persist.root_at(self.persist_name)
