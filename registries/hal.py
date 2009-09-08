#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import re
import string
import posixpath

from checkbox.lib.cache import cache
from checkbox.lib.dmi import Dmi, DmiNotAvailable
from checkbox.lib.pci import Pci

from checkbox.properties import String
from checkbox.registry import Registry
from checkbox.registries.command import CommandRegistry


class UnknownName(object):
    def __init__(self, function):
        self._function = function

    def __get__(self, instance, cls=None):
        self._instance = instance
        return self

    def __call__(self, *args, **kwargs):
        name = self._function(self._instance, *args, **kwargs)
        if name and name.startswith("Unknown ("):
            name = None

        return name


class DeviceRegistry(Registry):
    """Registry for HAL device information.

    Each item contained in this registry consists of the properties of
    the corresponding HAL device.
    """

    def __init__(self, properties):
        self._properties = properties

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self.items()]

        return "\n".join(strings)

    def _get_bus(self):
        return self._properties.get("linux.subsystem")

    def _get_category(self):
        if "system.hardware.vendor" in self._properties:
            return "SYSTEM"

        if "net.interface" in self._properties:
            return "NETWORK"

        if "pci.device_class" in self._properties:
            class_id = self._properties["pci.device_class"]
            subclass_id = self._properties["pci.device_subclass"]

            if class_id == Pci.BASE_CLASS_NETWORK:
                return "NETWORK"

            if class_id == Pci.BASE_CLASS_DISPLAY:
                return "VIDEO"

            if class_id == Pci.BASE_CLASS_SERIAL \
               and subclass_id == Pci.CLASS_SERIAL_USB:
                return "USB"

            if class_id == Pci.BASE_CLASS_STORAGE:
                if subclass_id == Pci.CLASS_STORAGE_SCSI:
                    return "SCSI"

                if subclass_id == Pci.CLASS_STORAGE_IDE:
                    return "IDE"

                if subclass_id == Pci.CLASS_STORAGE_FLOPPY:
                    return "FLOPPY"

                if subclass_id == Pci.CLASS_STORAGE_RAID:
                    return "RAID"

            if class_id == Pci.BASE_CLASS_COMMUNICATION \
               and subclass_id == Pci.CLASS_COMMUNICATION_MODEM:
                return "MODEM"

            if class_id == Pci.BASE_CLASS_INPUT \
               and subclass_id == Pci.CLASS_INPUT_SCANNER:
                return "SCANNER"

            if class_id == Pci.BASE_CLASS_MULTIMEDIA:
                if subclass_id == Pci.CLASS_MULTIMEDIA_VIDEO:
                    return "CAPTURE"

                if subclass_id == Pci.CLASS_MULTIMEDIA_AUDIO:
                    return "AUDIO"

            if class_id == Pci.BASE_CLASS_SERIAL \
               and subclass_id == Pci.CLASS_SERIAL_FIREWIRE:
                return "FIREWIRE"

            if class_id == Pci.BASE_CLASS_BRIDGE \
               and (subclass_id == Pci.CLASS_BRIDGE_PCMCIA \
                    or subclass_id == Pci.CLASS_BRIDGE_CARDBUS):
                return "SOCKET"

        if "info.capabilities" in self._properties:
            capabilities = self._properties["info.capabilities"]
            if "input.keyboard" in capabilities:
                return "KEYBOARD"

            if "input.mouse" in capabilities:
                return "MOUSE"

        if "storage.drive_type" in self._properties:
            drive_type = self._properties["storage.drive_type"]
            if drive_type == "cdrom":
                return "CDROM"

            if drive_type == "disk":
                return "DISK"

            if drive_type == "floppy":
                return "FLOPPY"

        if "scsi.type" in self._properties:
            type = self._properties["scsi.type"]
            if type == "disk":
                return "DISK"

            if type == "tape":
                return "TAPE"

            if type == "printer":
                return "PRINTER"

            if type == "cdrom":
                return "CDROM"

            if type == "scanner":
                return "SCANNER"

            if type == "raid":
                return "RAID"

        if self._get_product_id():
            return "OTHER"

        return None

    def _get_driver(self):
        return self._properties.get("info.linux.driver")

    def _get_path(self):
        return self._properties.get("linux.sysfs_path", "").replace("/sys", "")

    def _get_type(self):
        # Strip the string literals generated by HAL
        for property in ("ccwgroup.ctc.type",
                         "ccwgroup.lcs.type",
                         "ibmebus.type",
                         "mmc.type",
                         "net.arp_proto_hw_id",
                         "storage.firmware_version",
                         "system.hardware.version"):
            if property in self._properties:
                return self._properties[property]

        if "battery.type" in self._properties:
            name = self._properties["battery.type"]
            if name == "primary":
                name = "battery"
            return name

        if "info.category" in self._properties:
            category = self._properties["info.category"]
            if category == "bluetooth_acl":
                return "ACL"
            if category == "bluetooth_sco":
                return "SCO"
            if category == "bluetooth_hci":
                return "USB"

        if "killswitch.type" in self._properties:
            name = self._properties["killswitch.type"]
            if name == "wwan":
                name = "wimax"
            if name != "unknown":
                return name

        if "scsi.type" in self._properties:
            name = self._properties["scsi.type"]
            name_to_type = {
                "disk": "0",
                "tape": "1",
                "printer": "2",
                "processor": "3",
                "cdrom": "5",
                "scanner": "6",
                "medium_changer": "8",
                "comm": "9",
                "raid": "12"}
            if name in name_to_type:
                return name_to_type[name]

        if "usb_device.version" in self._properties:
            return "%.2f" % self._properties["usb_device.version"]

        return None

    def _get_vendor_id(self):
        if "info.subsystem" in self._properties:
            vendor_id = "%s.vendor_id" % self._properties["info.subsystem"]
            if vendor_id in self._properties:
                return self._properties[vendor_id]

        return None

    def _get_product_id(self):
        if "info.subsystem" in self._properties:
            product_id = "%s.product_id" % self._properties["info.subsystem"]
            if product_id in self._properties:
                return self._properties[product_id]

        # pnp
        if "pnp.id" in self._properties:
            match = re.match(r"^(?P<vendor_name>.*)(?P<product_id>[%s]{4})$"
                % string.hexdigits, self._properties["pnp.id"])
            if match:
                return int(match.group("product_id"), 16)

        return None

    def _get_subvendor_id(self):
        return self._properties.get("pci.subsys_vendor_id")

    def _get_subproduct_id(self):
        return self._properties.get("pci.subsys_product_id")

    @UnknownName
    def _get_vendor(self):
        bus = self._get_bus()

        # Ignore subsystems using parent or generated names
        if bus in ("drm", "pci", "rfkill", "usb"):
            return None

        # pnp
        if "pnp.id" in self._properties:
            match = re.match(r"^(?P<vendor_name>.*)(?P<product_id>[%s]{4})$"
                % string.hexdigits, self._properties["pnp.id"])
            if match:
                return match.group("vendor_name")

        for property in ("battery.vendor",
                         "ieee1394.vendor",
                         "scsi.vendor",
                         "system.hardware.vendor",
                         "info.vendor"):
            if property in self._properties:
                return self._properties[property]

        return None

    @UnknownName
    def _get_product(self):
        bus = self._get_bus()

        # Ignore subsystems using parent or generated names
        if bus in ("drm", "net", "platform", "pci", "pnp", "scsi_generic",
                   "scsi_host", "tty", "usb", "video4linux"):
            return None

        if "usb.interface.number" in self._properties:
            return None

        if self._properties.get("info.category") == "ac_adapter":
            return None

        for property in ("alsa.device_id",
                         "alsa.card_id",
                         "sound.card_id",
                         "battery.model",
                         "ieee1394.product",
                         "killswitch.name",
                         "oss.device_id",
                         "scsi.model",
                         "system.hardware.product",
                         "info.product"):
            if property in self._properties:
                return self._properties[property]

        return None

    def items(self):
        return (
            ("path", self._get_path()),
            ("bus", self._get_bus()),
            ("category", self._get_category()),
            ("driver", self._get_driver()),
            ("type", self._get_type()),
            ("vendor_id", self._get_vendor_id()),
            ("product_id", self._get_product_id()),
            ("subvendor_id", self._get_subvendor_id()),
            ("subproduct_id", self._get_subproduct_id()),
            ("vendor", self._get_vendor()),
            ("product", self._get_product()))


class DmiDeviceRegistry(DeviceRegistry):

    _category_to_property = {
        "BIOS": "system.firmware",
        "BOARD": "system.board",
        "CHASSIS": "system.chassis"}

    def __init__(self, properties, category):
        super(DmiDeviceRegistry, self).__init__(properties)
        if category not in self._category_to_property:
            raise Exception, "Unsupported category: %s" % category

        self._category = category

    @property
    def _property(self):
        return self._category_to_property[self._category]

    def _get_category(self):
        return self._category

    def _get_path(self):
        path = super(DmiDeviceRegistry, self)._get_path()
        return posixpath.join(path, self._category.lower())

    @DmiNotAvailable
    def _get_type(self):
        version_property = "%s.version" % self._property
        if version_property in self._properties:
            return self._properties[version_property]

        type_property = "%s.type" % self._property
        if type_property in self._properties:
            chassis_name = self._properties[type_property]
            return str(Dmi.chassis_names.index(chassis_name))

        return None

    @DmiNotAvailable
    def _get_vendor(self):
        for subproperty in "vendor", "manufacturer":
            property = "%s.%s" % (self._property, subproperty)
            if property in self._properties:
                return self._properties[property]

        return None

    @DmiNotAvailable
    def _get_product(self):
        product_property = "%s.product" % self._property
        if product_property in self._properties:
            return self._properties[product_property]

        return None


class HalRegistry(CommandRegistry):
    """Registry for HAL information.

    Each item contained in this registry consists of the udi as key and
    the corresponding device registry as value.
    """

    # Command to retrieve hal information.
    command = String(default="lshal")

    # See also section "Deprecated Properties" of the "HAL 0.5.10 Specification",
    # available from http://people.freedesktop.org/~david/hal-spec/hal-spec.html
    _deprecated_expressions = (
        (r"info\.bus",                             "info.subsystem"),
        (r"([^\.]+)\.physical_device",             "\1.originating_device"),
        (r"power_management\.can_suspend_to_ram",  "power_management.can_suspend"),
        (r"power_management\.can_suspend_to_disk", "power_management.can_hibernate"),
        (r"smbios\.system\.manufacturer",          "system.hardware.vendor"),
        (r"smbios\.system\.product",               "system.hardware.product"),
        (r"smbios\.system\.version",               "system.hardware.version"),
        (r"smbios\.system\.serial",                "system.hardware.serial"),
        (r"smbios\.system\.uuid",                  "system.hardware.uuid"),
        (r"smbios\.bios\.vendor",                  "system.firmware.vendor"),
        (r"smbios\.bios\.version",                 "system.firmware.version"),
        (r"smbios\.bios\.release_date",            "system.firmware.release_date"),
        (r"smbios\.chassis\.manufacturer",         "system.chassis.manufacturer"),
        (r"smbios\.chassis\.type",                 "system.chassis.type"),
        (r"system\.vendor",                        "system.hardware.vendor"),
        (r"usb_device\.speed_bcd",                 "usb_device.speed"),
        (r"usb_device\.version_bcd",               "usb_device.version"))

    def __init__(self, *args, **kwargs):
        super(HalRegistry, self).__init__(*args, **kwargs)
        self._deprecated_patterns = ((re.compile("^%s$" % a), b)
            for (a, b) in self._deprecated_expressions)

    def _get_key(self, key):
        for (old, new) in self._deprecated_patterns:
            key = old.sub(new, key)

        return key

    def _get_value(self, value, type):
        value = value.strip()
        if type == "bool":
            value = bool(value == "true")
        elif type == "double":
            value = float(value.split()[0])
        elif type == "int" or type == "uint64":
            value = int(value.split()[0])
        elif type == "string":
            value = str(value.strip("'"))
        elif type == "string list":
            value = [v.strip("'")
                    for v in value.strip("{}").split(", ")]
        else:
            raise Exception, "Unknown type: %s" % type

        return value

    def _ignore_device(self, device):
        # Ignore devices without bus information
        if not device.bus:
            return True

        # Ignore devices without product nor vendor information
        if not device.product and device.product_id is None \
           and not device.vendor and device.vendor_id is None:
            return True

        # Ignore virtual devices except for dmi information
        if device.bus != "dmi" \
           and "virtual" in device.path.split(posixpath.sep):
            return True

        return False

    @cache
    def items(self):
        items = []
        for record in self.split("\n\n"):
            if not record:
                continue

            name = None
            properties = {}
            for line in record.split("\n"):
                match = re.match(r"udi = '(.*)'", line)
                if match:
                    udi = match.group(1)
                    name = udi.split(posixpath.sep)[-1]
                    continue

                match = re.match(r"  (?P<key>.*) = (?P<value>.*) \((?P<type>.*?)\)", line)
                if match:
                    key = self._get_key(match.group("key"))
                    value = self._get_value(match.group("value"),
                        match.group("type"))
                    properties[key] = value

            if name == "computer":
                properties["linux.subsystem"] = "dmi"
                properties["linux.sysfs_path"] = "/sys/devices/virtual/dmi/id"

                device = DeviceRegistry(properties)
                items.append((device.path, device))
                for category in "BIOS", "BOARD", "CHASSIS":
                    device = DmiDeviceRegistry(properties, category)
                    items.append((device.path, device))
            else:
                device = DeviceRegistry(properties)
                if not self._ignore_device(device):
                    items.append((device.path, device))

        return items


factory = HalRegistry
