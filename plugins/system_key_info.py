from hwtest.plugin import Plugin


class SystemKeyInfo(Plugin):

    def register(self, manager):
        super(SystemKeyInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = self._manager.registry.system.key
        self._manager.reactor.fire(("report", "system_key"), message)


factory = SystemKeyInfo
