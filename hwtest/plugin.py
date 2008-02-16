import re
import logging

from hwtest.repository import Repository, RepositoryManager


class PluginManager(RepositoryManager):
    """
    Plugin manager which extends the repository to support the concepts
    of a reactor.
    """

    def __init__(self, config, registry, reactor):
        super(PluginManager, self).__init__(config)
        self.registry = registry
        self.reactor = reactor

        # Load sections
        sections = self._config.get_defaults().plugins
        for section_name in re.split(r"\s+", sections):
            section = self.load_section(section_name)
            for module in section.load_all():
                logging.debug("Registering %s", module.name)
                module.register(self)


class Plugin(Repository):
    """
    Plugin base class which should be inherited by each plugin
    implementation. This class extends the repository to automatically
    call the run method if defined.
    """

    def register(self, manager):
        self._manager = manager
        if hasattr(self, "run"):
            manager.reactor.call_on("run", self.run)
