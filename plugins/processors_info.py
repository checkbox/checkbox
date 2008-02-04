from hwtest.plugin import Plugin


class ProcessorsInfo(Plugin):

    def register(self, manager):
        super(ProcessorsInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = self._manager.registry.cpuinfo
        self._manager.reactor.fire(("report", "processors"), message)


factory = ProcessorsInfo
