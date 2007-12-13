from hwtest.plugin import Plugin


class RegistryInfo(Plugin):

    def register(self, manager):
        super(RegistryInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        # Recursively evaluate a false expression to walk the registry.
        self._manager.registry.eval_recursive("False")


factory = RegistryInfo
