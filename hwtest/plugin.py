import os
import logging

from hwtest.log import format_object


class PluginManager(object):
    def __init__(self, reactor, message_store, persist, persist_filename=None):
        self.reactor = reactor
        self.message_store = message_store
        self._plugins = []
        self._error = None

        self.persist = persist
        self._persist_filename = persist_filename
        if persist_filename and os.path.exists(persist_filename):
            self.persist.load(persist_filename)

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
