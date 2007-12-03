from hwtest.plugin import Plugin


class SystemKeyInfo(Plugin):

    def register(self, manager):
        super(SystemKeyInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "system_key"), message)

    def create_message(self):
        return self._manager.registry.system.key


factory = SystemKeyInfo
