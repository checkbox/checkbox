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
        message = self.create_message()
        self._manager.reactor.fire(("report", "device"), message)

    def create_message(self):
        message = {}
        message["devices"] = []
        message["version"] = self._device_manager.get_version()
        for device in self._device_manager.get_devices():
            message["devices"].append(device.properties)

        return message

factory = DeviceInfo
