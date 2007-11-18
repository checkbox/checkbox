from hwtest.plugin import Plugin


class ProcessorInfo(Plugin):

    def register(self, manager):
        super(ProcessorInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "processor"), message)

    def create_message(self):
        return self._manager.registry.cpuinfo


factory = ProcessorInfo
