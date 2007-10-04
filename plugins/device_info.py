import dbus
import md5

from commands import getoutput
from operator import indexOf
from string import rsplit

from hwtest.plugin import Plugin
from hwtest.report_helpers import createDevice, createProperty, createElement

class Device(object):

    def __init__(self, id, udi, parent, properties):
        self.id = id
        self.udi = udi
        self.parent = parent
        self.parent_device = None
        self.properties = properties
        self.children = []

    def add_child(self, device):
        self.children.append(device)
        device.parent = self

    def toxml(self, report, parent):
        if self.parent:
            device = createDevice(report, parent, self.id, self.udi,
                                  self.parent.id)
        else:
            device = createDevice(report, parent, self.id, self.udi)

        properties = createElement(report, 'properties', device)

        keys = self.properties.keys()
        keys.sort()
        for key in keys:
            value = self.properties[key]
            createProperty(report, properties, key, value)

class DeviceManager(object):

    def __init__(self):
        # Get HAL version
        hald = getoutput('/usr/sbin/hald --version')
        self.hal_version = hald.rsplit(': ')[1]

        self._bus = dbus.SystemBus()
        self._manager_obj = self._bus.get_object("org.freedesktop.Hal",
                                                 "/org/freedesktop/Hal/Manager")
        self._manager = dbus.Interface(self._manager_obj,
                                  "org.freedesktop.Hal.Manager")
        self.devices = []
        self.computer_id = None
        self.refreshDevices()

    def refreshDevices(self):
        
        # Build list of devices       
        device_list = self._manager.GetAllDevices()
        for device in device_list:
            id = indexOf(device_list, device)
            device_obj = self._bus.get_object("org.freedesktop.Hal", device)
            properties = device_obj.GetAllProperties(dbus_interface="org.freedesktop.Hal.Device")
            parent = properties.get("info.parent")
            if parent:
                self.computer_id = id
            self.devices.append(Device(id, device, parent, properties))
        
        # Create parent and child relationships
        for device in self.devices:
            parent = device.parent
            if parent:
                for p in self.devices:
                    if p.udi == parent:
                        p.add_child(device)

    def toxml(self, report):
        hardware = createElement(report, 'hardware', report.root)
        report.hardware = hardware
        hal = createElement(report, 'hal', hardware)
        version = hal.setAttribute('version', str(self.hal_version))
        for device in self.devices:
            device.toxml(report, hal)


class DeviceInfo(Plugin):

    def __init__(self, config, device_manager=None):
        super(DeviceInfo, self).__init__(config)
        self._device_manager = device_manager or DeviceManager()

    def gather(self):
        report = self._manager.report
        if not report.finalised:
            udi = '/org/freedesktop/Hal/devices/computer'
            computer = filter(lambda d: d.properties['info.udi'] == udi,
                self._device_manager.devices)[0]

            # Generate system fingerprint
            fingerprint = md5.new()
            fingerprint.update(computer.properties['system.vendor'])
            fingerprint.update(computer.properties['system.product'])

            # Store summary information
            if not report.info.has_key('architecture'):
                report.info['architecture'] = computer.properties['system.kernel.machine']

            report.info['system_id'] = fingerprint.hexdigest()

            self._device_manager.toxml(self._manager.report)


factory = DeviceInfo
