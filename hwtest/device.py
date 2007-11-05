from dbus import Interface


class Device(object):

    def __init__(self, hal_device):
        self._children = []
        self._device = hal_device
        self.properties = hal_device.GetAllProperties()
        self.udi = self.properties["info.udi"]
        self.parent = None

    def add_child(self, device):
        self._children.append(device)
        device.parent = self

    def get_children(self):
        return self._children


class DeviceManager(object):

    def __init__(self, bus=None):
        self._bus = bus
        self._manager = None
        self._version = None
        self._devices = []

    def _get_bus(self):
        if not self._bus:
            from dbus import SystemBus
            self._bus = SystemBus()

        return self._bus

    def _get_manager(self):
        if not self._manager:
            manager = self._get_bus().get_object("org.freedesktop.Hal",
                                                 "/org/freedesktop/Hal/Manager")
            self._manager = Interface(manager, "org.freedesktop.Hal.Manager")

        return self._manager

    def get_version(self):
        if not self._version:
            from commands import getoutput
            version = getoutput('/usr/sbin/hald --version')
            self._version = version.rsplit(': ')[1]

        return self._version

    def _create_device(self, hal_device):
        hal_device = Interface(hal_device, "org.freedesktop.Hal.Device")
        device = Device(hal_device)
        return device

    def get_devices_by_match(self, key, value):
        devices = []
        for match in self._get_manager().FindDeviceStringMatch(key, value):
            hal_device = self._get_bus().get_object("org.freedesktop.Hal", match)
            devices.append(self._create_device(hal_device))

        return devices

    def get_device_by_udi(self, value):
        return self.get_devices_by_match("info.udi", value)[0]

    def get_devices(self):
        if not self._devices:
            for udi in self._get_manager().GetAllDevices():
                hal_device = self._get_bus().get_object("org.freedesktop.Hal", udi)
                device = self._create_device(hal_device)
                self._devices.append(device)

        return self._devices
