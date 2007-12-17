import os
import re

from hwtest.repository import Repository, RepositoryManager


class PluginManager(RepositoryManager):
    """
    Plugin manager which extends the repository to support the concepts
    of a reactor and persistence.
    """

    def __init__(self, config, registry, reactor, persist,
                 persist_filename=None):
        super(PluginManager, self).__init__(config)
        self.registry = registry
        self.reactor = reactor

        # Load persistence
        self.persist = persist
        self._persist_filename = persist_filename
        if persist_filename and os.path.exists(persist_filename):
            self.persist.load(persist_filename)

        # Load sections
        sections = self._config.get_defaults().plugins
        for section_name in re.split(r"\s+", sections):
            section = self.load_section(section_name)
            for name in section.load_all():
                name.register(self)

    def flush(self):
        self.reactor.fire("flush")
        self._save_persist()

    def _save_persist(self):
        if self._persist_filename:
            self.persist.save(self._persist_filename)


class Plugin(Repository):
    """
    Plugin base class which should be inherited by each plugin
    implementation. This class extends the repository to automatically
    call the run method if defined and persistence if persist_name
    is defined.
    """

    persist_name = None

    def register(self, manager):
        self._manager = manager
        if hasattr(self, "run"):
            manager.reactor.call_on("run", self.run)
        if self.persist_name is not None:
            self._persist = manager.persist.root_at(self.persist_name)
