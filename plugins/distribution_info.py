from hwtest.plugin import Plugin


class DistributionInfo(Plugin):

    def register(self, manager):
        super(DistributionInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = self._manager.registry.lsb
        self._manager.reactor.fire(("report", "distribution"), message)


factory = DistributionInfo
