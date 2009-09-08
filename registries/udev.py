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
import os
import re
import string
import posixpath

from curses.ascii import isprint

from checkbox.lib.bit import get_bitmask, test_bit
from checkbox.lib.cache import cache
from checkbox.lib.dmi import DmiNotAvailable
from checkbox.lib.input import Input
from checkbox.lib.pci import Pci

from checkbox.properties import String
from checkbox.registry import Registry
from checkbox.registries.command import CommandRegistry
from checkbox.registries.link import LinkRegistry
from checkbox.registries.map import MapRegistry


class DeviceRegistry(Registry):

    def __init__(self, environment, attributes):
        super(DeviceRegistry, self).__init__()
        self._environment = environment
        self._attributes = attributes

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self.items()
            if not isinstance(v, Registry)]

        return "\n".join(strings)

    def _get_bus(self):
        sys_path = posixpath.join("/sys%s" % self._environment["DEVPATH"], "subsystem")
        if posixpath.islink(sys_path):
            link = os.readlink(sys_path)
            if "/" in link:
                return posixpath.basename(link)

        return None

    def _get_category(self):
        if "sys_vendor" in self._attributes:
            return "SYSTEM"

        if "IFINDEX" in self._environment:
            return "NETWORK"

        if "PCI_CLASS" in self._environment:
            pci_class = self._environment["PCI_CLASS"]
            prog_if = int(pci_class[-2:], 16)
            subclass_id = int(pci_class[-4:-2], 16)
            class_id = int(pci_class[:-4], 16)

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

        if "ID_TYPE" in self._environment:
            id_type = self._environment["ID_TYPE"]

            if id_type == "cd":
                return "CDROM"

            if id_type == "disk":
                return "DISK"

            if id_type == "video":
                return "VIDEO"

        if "KEY" in self._environment:
            key = self._environment["KEY"].strip("=")
            bitmask = get_bitmask(key)

            for i in range(Input.KEY_Q, Input.KEY_P+1):
                if not test_bit(i, bitmask):
                    break
            else:
                return "KEYBOARD"

            if test_bit(Input.BTN_MOUSE, bitmask):
                return "MOUSE"

        if self._environment.get("DEVTYPE") == "disk":
            if "ID_CDROM" in self._environment:
                return "CDROM"

            if "ID_DRIVE_FLOPPY" in self._environment:
                return "FLOPPY"

        if self._environment.get("DEVTYPE") == "scsi_device":
            type = int(self._get_type())
            if type in (0, 7, 14):
                return "DISK"

            if type == 1:
                return "TAPE"

            if type == 2:
                return "PRINTER"

            if type in (4, 5):
                return "CDROM"

            if type == 6:
                return "SCANNER"

            if type == 12:
                return "RAID"

        if self._get_product_id():
            return "OTHER"

        return None

    def _get_driver(self):
        if "DRIVER" in self._environment:
            return self._environment["DRIVER"]

        if "ID_USB_DRIVER" in self._environment:
            return self._environment["ID_USB_DRIVER"]

        return None

    def _get_path(self):
        return self._environment.get("DEVPATH")

    def _get_type(self):
        if "type" in self._attributes:
            return self._attributes.get("type").lower()

        for attribute in "product_version", "rev":
            if attribute in self._attributes:
                return self._attributes[attribute]

        bus = self._get_bus()
        if bus != "pci" and "version" in self._attributes:
            return self._attributes.get("version")

        return None

    def _get_vendor_id(self):
        # pci
        if "PCI_ID" in self._environment:
            vendor_id, product_id = self._environment["PCI_ID"].split(":")
            return int(vendor_id, 16)

        # usb interface
        if "PRODUCT" in self._environment \
           and self._environment.get("DEVTYPE") == "usb_interface":
            vendor_id, product_id, revision = self._environment["PRODUCT"].split("/")
            return int(vendor_id, 16)

        # usb device
        if "idVendor" in self._attributes:
            return int(self._attributes["idVendor"], 16)

        # ieee1394
        vendor_id_path = posixpath.join(self._get_path(), "../vendor_id")
        if posixpath.exists(vendor_id_path):
            vendor_id = open(vendor_id_path, "r").read().strip()
            return int(vendor_id, 16)

        return None

    def _get_product_id(self):
        # pci
        if "PCI_ID" in self._environment:
            vendor_id, product_id = self._environment["PCI_ID"].split(":")
            return int(product_id, 16)

        # usb interface
        if "PRODUCT" in self._environment \
           and self._environment.get("DEVTYPE") == "usb_interface":
            vendor_id, product_id, revision = self._environment["PRODUCT"].split("/")
            return int(product_id, 16)

        # usb device and ieee1394
        for attribute in "idProduct", "model_id":
            if attribute in self._attributes:
                return int(self._attributes[attribute], 16)

        # pnp
        if "id" in self._attributes:
            match = re.match(r"^(?P<vendor_name>.*)(?P<product_id>[%s]{4})$"
                % string.hexdigits, self._attributes["id"])
            if match:
                return int(match.group("product_id"), 16)

        return None

    def _get_subvendor_id(self):
        if "PCI_SUBSYS_ID" in self._environment:
            pci_subsys_id = self._environment["PCI_SUBSYS_ID"]
            subvendor_id, subproduct_id = pci_subsys_id.split(":")
            return int(subvendor_id, 16)

        return None

    def _get_subproduct_id(self):
        if "PCI_SUBSYS_ID" in self._environment:
            pci_subsys_id = self._environment["PCI_SUBSYS_ID"]
            subvendor_id, subproduct_id = pci_subsys_id.split(":")
            return int(subproduct_id, 16)

        return None

    def _get_vendor(self):
        if "RFKILL_NAME" in self._environment:
            return None

        if "POWER_SUPPLY_MANUFACTURER" in self._environment:
            return self._environment["POWER_SUPPLY_MANUFACTURER"]

        if "vendor" in self._attributes:
            vendor = self._attributes["vendor"]
            if not re.match(r"^0x[%s]{4}$" % string.hexdigits, vendor):
                return vendor

        # dmi
        if "sys_vendor" in self._attributes:
            return self._attributes["sys_vendor"]

        # pnp
        if "id" in self._attributes:
            match = re.match(r"^(?P<vendor_name>.*)(?P<product_id>[%s]{4})$"
                % string.hexdigits, self._attributes["id"])
            if match:
                return match.group("vendor_name")

        # ieee1394
        vendor_path = posixpath.join(self._get_path(), "../vendor_oui")
        if posixpath.exists(vendor_path):
            return open(vendor_path, "r").read().strip()

        return None

    def _get_product(self):
        for element in ("NAME",
                        "RFKILL_NAME",
                        "POWER_SUPPLY_MODEL_NAME"):
            if element in self._environment:
                return self._environment[element].strip('"')

        for attribute in ("description",
                          "model_name_kv",
                          "model",
                          "product_name"):
            if attribute in self._attributes:
                return self._attributes[attribute]

        # sound
        bus = self._get_bus()
        if bus == "sound":
            device = posixpath.basename(self._environment["DEVPATH"])
            match = re.match(r"(card|controlC|hwC|midiC)(?P<card>\d+)", device)
            if match:
                card = match.group("card")
                in_card = False
                file = open("/proc/asound/cards", "r")
                for line in file.readlines():
                    line = line.strip()
                    match = re.match(r"(?P<card>\d+) \[", line)
                    if match:
                        in_card = match.group("card") == card

                    if in_card:
                        match = re.match(r"""(?P<name>.*) """
                            """at (?P<address>0x[%s]{8}) """
                            """irq (?P<irq>\d+)""" % string.hexdigits, line)
                        if match:
                            return match.group("name")

            path = None
            match = re.match(r"pcmC(?P<card>\d+)D(?P<device>\d+)(?P<type>\w)",
                device)
            if match:
                path = "/proc/asound/card%s/pcm%s%c/info" % match.groups()

            match = re.match(r"(dsp|adsp|midi|amidi|audio|mixer)(?P<card>\d+)?",
                device)
            if match:
                card = match.group("card") or 0
                path = "/proc/asound/card%s/pcm0p/info" % card

            if path:
                file = open(path, "r")
                for line in file.readlines():
                    match = re.match(r"name: (?P<name>.*)", line)
                    if match:
                        return match.group("name")

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
            ("product", self._get_product()),
            ("attributes", MapRegistry(self._attributes)),
            ("device", LinkRegistry(self)))


class DmiDeviceRegistry(DeviceRegistry):

    def __init__(self, environment, attributes, category):
        super(DmiDeviceRegistry, self).__init__(environment, attributes)
        self._category = category

    def _get_category(self):
        return self._category

    def _get_path(self):
        path = super(DmiDeviceRegistry, self)._get_path()
        return posixpath.join(path, self._category.lower())

    @DmiNotAvailable
    def _get_type(self):
        for name in "type", "version":
            attribute = "%s_%s" % (self._category.lower(), name)
            if attribute in self._attributes:
                return self._attributes[attribute]

        return None

    @DmiNotAvailable
    def _get_product(self):
        attribute = "%s_name" % self._category.lower()
        if attribute in self._attributes:
            return self._attributes[attribute]

        return None

    @DmiNotAvailable
    def _get_vendor(self):
        attribute = "%s_vendor" % self._category.lower()
        if attribute in self._attributes:
            return self._attributes[attribute]

        return None


class UdevRegistry(CommandRegistry):
    """Registry for udev information."""

    # Command to retrieve udev information.
    command = String(default="udevadm info --export-db")

    def _get_attributes(self, path):
        attributes = {}
        sys_path = "/sys%s" % path
        try:
            names = os.listdir(sys_path)
        except OSError:
            return attributes

        for name in names:
            name_path = posixpath.join(sys_path, name)
            if name[0] == "." \
               or name in ["dev", "uevent"] \
               or posixpath.isdir(name_path) \
               or posixpath.islink(name_path):
                continue

            try:
                value = open(name_path, "r").read().strip()
            except IOError:
                continue

            value = value.split("\n")[0]
            if [c for c in value if not isprint(c)]:
                continue

            attributes[name] = value

        return attributes

    def _ignore_device(self, device):
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
        line_pattern = re.compile(r"(?P<key>\w):\s*(?P<value>.*)")
        multi_pattern = re.compile(r"(?P<key>\w+)=(?P<value>.*)")

        for record in str(self).split("\n\n"):
            if not record:
                continue

            # Determine path and environment
            path = None
            environment = {}
            for line in record.split("\n"):
                match = line_pattern.match(line)
                if not match:
                    raise Exception, \
                        "Device line not supported: %s" % line

                key = match.group("key")
                value = match.group("value")

                if key == "P":
                    path= value
                elif key == "E":
                    match = multi_pattern.match(value)
                    if not match:
                        raise Exception, \
                            "Device property not supported: %s" % value
                    environment[match.group("key")] = match.group("value")

            # Determine attributes
            attributes = self._get_attributes(path)

            if path == "/devices/virtual/dmi/id":
                device = DeviceRegistry(environment, attributes)
                items.append((path, device))
                for category in "BIOS", "BOARD", "CHASSIS":
                    device = DmiDeviceRegistry(environment, attributes, category)
                    items.append((device.path, device))
            else:
                device = DeviceRegistry(environment, attributes)
                if not self._ignore_device(device):
                    items.append((path, device))

        return items


factory = UdevRegistry
