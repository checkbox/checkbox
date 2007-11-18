from hwtest.plugin import Plugin


class SystemIdInfo(Plugin):

    def register(self, manager):
        super(SystemIdInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "system_id"), message)

    def create_message(self):
        return self._manager.registry.system.id


factory = SystemIdInfo
