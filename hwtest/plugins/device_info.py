from hwtest.plugin import Plugin
from hwtest.device import DeviceManager


class DeviceInfo(Plugin):

    def __init__(self, device_manager=None):
        super(DeviceInfo, self).__init__()
        self._device_manager = device_manager or DeviceManager()

    def register(self, manager):
        self._manager = manager
        self._manager.reactor.call_on("gather_information", self.gather_information)
        self._manager.reactor.call_on("run", self.run)

    def create_message(self):
        device_info = self._device_info
        self._device_info = []
        return {"type": "device-info", "device-info": device_info}

    def gather_information(self):
        message = self.create_message()
        if len(message["device-info"]):
               self._manager.message_store.add(message)

    def run(self):
        self._device_info = []

        for device in self._device_manager.get_devices():
            self._device_info.append(device.properties)
