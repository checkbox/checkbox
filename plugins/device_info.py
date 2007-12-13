from hwtest.plugin import Plugin


class DeviceInfo(Plugin):

    def register(self, manager):
        super(DeviceInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = {}
        message["version"] = self._manager.registry.hald.version
        message["devices"] = self._manager.registry.hal
        self._manager.reactor.fire(("report", "device"), message)


factory = DeviceInfo
