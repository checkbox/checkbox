from hwtest.plugin import Plugin
from hwtest.processor import ProcessorManager


class ProcessorInfo(Plugin):

    def __init__(self, config, processor_manager=None):
        super(ProcessorInfo, self).__init__(config)
        self._processor_manager = processor_manager or ProcessorManager()

    def register(self, manager):
        super(ProcessorInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "set-processors"), message)

    def create_message(self):
        return self._processor_manager.get_processors()


factory = ProcessorInfo
