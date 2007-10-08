from hwtest.plugin import Plugin
from hwtest.device import DeviceManager


class DeviceInfo(Plugin):

    def __init__(self, config, device_manager=None):
        super(DeviceInfo, self).__init__(config)
        self._device_manager = device_manager or DeviceManager()

    def register(self, manager):
        super(DeviceInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        self._manager.reactor.fire(("report", "set-device-manager"),
            self._device_manager)


factory = DeviceInfo
