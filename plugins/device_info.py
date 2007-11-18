from hwtest.plugin import Plugin


class DeviceInfo(Plugin):

    def register(self, manager):
        super(DeviceInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = self.create_message()
        self._manager.reactor.fire(("report", "device"), message)

    def create_message(self):
        message = {}
        message["version"] = self._manager.registry.hald.version
        message["devices"] = self._manager.registry.hal

        return message

factory = DeviceInfo
