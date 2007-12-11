from hwtest.plugin import Plugin


class DistributionInfo(Plugin):

    def register(self, manager):
        super(DistributionInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self._manager.registry.lsb
        self._manager.reactor.fire(("report", "distribution"), message)


factory = DistributionInfo
