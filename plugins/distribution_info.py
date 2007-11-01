from hwtest.distribution import get_distribution
from hwtest.plugin import Plugin


class DistributionInfo(Plugin):

    def register(self, manager):
        super(DistributionInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = get_distribution()
        self._manager.reactor.fire(("report", "distribution"), message)


factory = DistributionInfo
