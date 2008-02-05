from hwtest.plugin import Plugin


class PackagesInfo(Plugin):

    def register(self, manager):
        super(PackagesInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = self._manager.registry.packages
        self._manager.reactor.fire(("report", "packages"), message)


factory = PackagesInfo
