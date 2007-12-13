from hwtest.plugin import Plugin


class ProcessorInfo(Plugin):

    def register(self, manager):
        super(ProcessorInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = self._manager.registry.cpuinfo
        self._manager.reactor.fire(("report", "processor"), message)


factory = ProcessorInfo
