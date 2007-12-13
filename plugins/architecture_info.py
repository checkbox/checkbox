from hwtest.plugin import Plugin


class ArchitectureInfo(Plugin):

    def register(self, manager):
        super(ArchitectureInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = self._manager.registry.dpkg.architecture
        self._manager.reactor.fire(("report", "architecture"), message)


factory = ArchitectureInfo
