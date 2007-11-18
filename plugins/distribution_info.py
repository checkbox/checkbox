from hwtest.distribution import get_distribution
from hwtest.plugin import Plugin


class DistributionInfo(Plugin):

    def register(self, manager):
        super(DistributionInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "distribution"), message)

    def create_message(self):
        return self._manager.registry.lsb


factory = DistributionInfo
