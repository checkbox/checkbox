#
# This file is part of Checkbox.
#
# Copyright 2011 Canonical Ltd.
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
from checkbox.lib.dmi import Dmi, DmiNotAvailable
from checkbox.lib.input import Input
from checkbox.lib.pci import Pci
from checkbox.lib.usb import Usb


class UdevDevice(object):
    __slots__ = ("_environment", "_attributes", "_stack")

    def __init__(self, environment, attributes, stack=[]):
        super(UdevDevice, self).__init__()
        self._environment = environment
        self._attributes = attributes
        self._stack = stack

    @property
    def bus(self):
        return self._environment.get("SUBSYSTEM")

    @property
    def category(self):
        if "sys_vendor" in self._attributes:
            return "SYSTEM"

        if "IFINDEX" in self._environment:
            return "NETWORK"

        if "PCI_CLASS" in self._environment:
            pci_class_string = self._environment["PCI_CLASS"]
            pci_class = int(pci_class_string, 16)

            # Strip prog_if if defined
            if pci_class > 0xFFFF:
                pci_class >>= 8

            subclass_id = pci_class & 0xFF
            class_id = (pci_class >> 8) & 0xFF

            if class_id == Pci.BASE_CLASS_NETWORK:
                if subclass_id == Pci.CLASS_NETWORK_WIRELESS:
                    return "WIRELESS"
                else:
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

                if subclass_id == Pci.CLASS_MULTIMEDIA_AUDIO \
                   or subclass_id == Pci.CLASS_MULTIMEDIA_AUDIO_DEVICE:
                    return "AUDIO"

            if class_id == Pci.BASE_CLASS_SERIAL \
               and subclass_id == Pci.CLASS_SERIAL_FIREWIRE:
                return "FIREWIRE"

            if class_id == Pci.BASE_CLASS_BRIDGE \
               and (subclass_id == Pci.CLASS_BRIDGE_PCMCIA \
                    or subclass_id == Pci.CLASS_BRIDGE_CARDBUS):
                return "SOCKET"

        if "bInterfaceClass" in self._attributes:
            interface_class = int(
                self._attributes["bInterfaceClass"], 16)
            interface_subclass = int(
                self._attributes["bInterfaceSubClass"], 16)
            interface_protocol = int(
                self._attributes["bInterfaceProtocol"], 16)

            if interface_class == Usb.BASE_CLASS_AUDIO:
                return "AUDIO"

            if interface_class == Usb.BASE_CLASS_PRINTER:
                return "PRINTER"

            if interface_class == Usb.BASE_CLASS_STORAGE:
                if interface_subclass == Usb.CLASS_STORAGE_FLOPPY:
                    return "FLOPPY"

                if interface_subclass == Usb.CLASS_STORAGE_SCSI:
                    return "SCSI"

            if interface_class == Usb.BASE_CLASS_VIDEO:
                return "CAPTURE"

            if interface_class == Usb.BASE_CLASS_WIRELESS:
                if interface_protocol == Usb.PROTOCOL_BLUETOOTH:
                    return "BLUETOOTH"
                else:
                    return "WIRELESS"

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

            for i in range(Input.KEY_Q, Input.KEY_P + 1):
                if not test_bit(i, bitmask):
                    break
            else:
                return "KEYBOARD"

            if test_bit(Input.BTN_TOUCH, bitmask):
                return "TOUCH"

            if test_bit(Input.BTN_MOUSE, bitmask):
                return "MOUSE"

        if "DEVTYPE" in self._environment:
            devtype = self._environment["DEVTYPE"]
            if devtype == "disk":
                if "ID_CDROM" in self._environment:
                    return "CDROM"

                if "ID_DRIVE_FLOPPY" in self._environment:
                    return "FLOPPY"

            if devtype == "scsi_device":
                type = int(self._attributes.get("type", "-1"))
                # Check for FLASH drives, see /lib/udev/rules.d/80-udisks.rules
                if type in (0, 7, 14) \
                   and not any(d.driver == "rts_pstor" for d in self._stack):
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

        if "DRIVER" in self._environment:
            if self._environment["DRIVER"] == "floppy":
                return "FLOPPY"

        if self.product:
            return "OTHER"

        return None

    @property
    def driver(self):
        if "DRIVER" in self._environment:
            return self._environment["DRIVER"]

        if "ID_USB_DRIVER" in self._environment:
            return self._environment["ID_USB_DRIVER"]

        return None

    @property
    def path(self):
        return self._environment.get("DEVPATH")

    @property
    def product_id(self):
        # pci
        if "PCI_ID" in self._environment:
            vendor_id, product_id = self._environment["PCI_ID"].split(":")
            return int(product_id, 16)

        # usb interface
        if "PRODUCT" in self._environment \
           and self._environment.get("DEVTYPE") == "usb_interface":
            vendor_id, product_id, revision \
                = self._environment["PRODUCT"].split("/")
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

    @property
    def vendor_id(self):
        # pci
        if "PCI_ID" in self._environment:
            vendor_id, product_id = self._environment["PCI_ID"].split(":")
            return int(vendor_id, 16)

        # usb interface
        if "PRODUCT" in self._environment \
           and self._environment.get("DEVTYPE") == "usb_interface":
            vendor_id, product_id, revision \
                = self._environment["PRODUCT"].split("/")
            return int(vendor_id, 16)

        # usb device
        if "idVendor" in self._attributes:
            return int(self._attributes["idVendor"], 16)

        return None

    @property
    def subproduct_id(self):
        if "PCI_SUBSYS_ID" in self._environment:
            pci_subsys_id = self._environment["PCI_SUBSYS_ID"]
            subvendor_id, subproduct_id = pci_subsys_id.split(":")
            return int(subproduct_id, 16)

        return None

    @property
    def subvendor_id(self):
        if "PCI_SUBSYS_ID" in self._environment:
            pci_subsys_id = self._environment["PCI_SUBSYS_ID"]
            subvendor_id, subproduct_id = pci_subsys_id.split(":")
            return int(subvendor_id, 16)

        return None

    @property
    def product(self):
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

        # floppy
        if self.driver == "floppy":
            return "Platform Device"

        return None

    @property
    def vendor(self):
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

        return None


class UdevLocalDevice(UdevDevice):

    @property
    def bus(self):
        sys_path = posixpath.join(
            "/sys%s" % self._environment["DEVPATH"], "subsystem")
        if posixpath.islink(sys_path):
            link = os.readlink(sys_path)
            if "/" in link:
                return posixpath.basename(link)

        return None

    @property
    def vendor_id(self):
        vendor_id = super(UdevLocalDevice, self).vendor_id
        if vendor_id is not None:
            return vendor_id

        # ieee1394
        vendor_id_path = posixpath.join(self.path, "../vendor_id")
        if posixpath.exists(vendor_id_path):
            vendor_id = open(vendor_id_path, "r").read().strip()
            return int(vendor_id, 16)

        return None

    @property
    def product(self):
        product = super(UdevLocalDevice, self).product
        if product is not None:
            return product

        # sound
        bus = self.bus
        if bus == "sound":
            device = posixpath.basename(self._environment["DEVPATH"])
            match = re.match(
                r"(card|controlC|hwC|midiC)(?P<card>\d+)", device)
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
            match = re.match(
                r"pcmC(?P<card>\d+)D(?P<device>\d+)(?P<type>\w)", device)
            if match:
                path = "/proc/asound/card%s/pcm%s%c/info" % match.groups()

            match = re.match(
                r"(dsp|adsp|midi|amidi|audio|mixer)(?P<card>\d+)?", device)
            if match:
                card = match.group("card") or 0
                path = "/proc/asound/card%s/pcm0p/info" % card

            if path and posixpath.exists(path):
                file = open(path, "r")
                for line in file.readlines():
                    match = re.match(r"name: (?P<name>.*)", line)
                    if match:
                        return match.group("name")

        return None

    @property
    def vendor(self):
        vendor = super(UdevLocalDevice, self).vendor
        if vendor is not None:
            return vendor

        # ieee1394
        vendor_path = posixpath.join(self.path, "../vendor_oui")
        if posixpath.exists(vendor_path):
            return open(vendor_path, "r").read().strip()

        return None


class UdevDmiDevice(UdevDevice):

    def __init__(self, environment, attributes, category):
        super(UdevDmiDevice, self).__init__(environment, attributes)
        self._category = category

    @property
    def category(self):
        return self._category

    @property
    def path(self):
        path = super(UdevDmiDevice, self).path
        return posixpath.join(path, self._category.lower())

    @property
    def product(self):
        if self._category == "CHASSIS":
            type_string = self._attributes.get("chassis_type", "0")
            type_index = int(type_string)
            return Dmi.chassis_names[type_index]

        for name in "name", "version":
            attribute = "%s_%s" % (self._category.lower(), name)
            product = self._attributes.get(attribute)
            if product and product != "Not Available":
                return product

        return None

    @DmiNotAvailable
    def _getVendor(self):
        attribute = "%s_vendor" % self._category.lower()
        if attribute in self._attributes:
            return self._attributes[attribute]

        return None

    @property
    def vendor(self):
        return self._getVendor()


class UdevParser(object):
    """udevadm parser."""

    device_factory = UdevDevice
    dmi_device_factory = UdevDmiDevice

    def __init__(self, stream):
        self.stream = stream
        self.stack = []

    def _ignoreDevice(self, device):
        # Ignore devices without bus information
        if not device.bus:
            return True

        # Ignore devices without product information
        if not device.product and device.product_id is None:
            return True

        # Ignore invalid subsystem information
        if ((device.subproduct_id is None
             and device.subvendor_id is not None)
            or (device.subproduct_id is not None
             and device.subvendor_id is None)):
            return True

        # Ignore virtual devices except for dmi information
        if device.bus != "dmi" \
           and "virtual" in device.path.split(posixpath.sep):
            return True

        return False

    def getAttributes(self, path):
        return {}

    def run(self, result):
        line_pattern = re.compile(r"(?P<key>\w):\s*(?P<value>.*)")
        multi_pattern = re.compile(r"(?P<key>[^=]+)=(?P<value>.*)")

        output = self.stream.read()
        for record in output.split("\n\n"):
            if not record:
                continue

            # Determine path and environment
            path = None
            environment = {}
            for line in record.split("\n"):
                if not line:
                    continue

                match = line_pattern.match(line)
                if not match:
                    raise Exception(
                        "Device line not supported: %s" % line)

                key = match.group("key")
                value = match.group("value")

                if key == "P":
                    path = value
                elif key == "E":
                    match = multi_pattern.match(value)
                    if not match:
                        raise Exception(
                            "Device property not supported: %s" % value)
                    environment[match.group("key")] = match.group("value")

            # Update stack
            while self.stack:
                if self.stack[-1].path + "/" in path:
                    break
                self.stack.pop()

            # Set default DEVPATH
            environment.setdefault("DEVPATH", path)

            # Determine attributes
            attributes = self.getAttributes(path)

            if path == "/devices/virtual/dmi/id":
                device = self.device_factory(environment, attributes)
                if not self._ignoreDevice(device):
                    result.addDevice(device)
                for category in "BIOS", "BOARD", "CHASSIS":
                    device = self.dmi_device_factory(
                        environment, attributes, category)
                    if not self._ignoreDevice(device):
                        result.addDevice(device)
            else:
                device = self.device_factory(environment, attributes, self.stack)
                if not self._ignoreDevice(device):
                    result.addDevice(device)

            self.stack.append(device)


class UdevLocalParser(UdevParser):

    device_factory = UdevLocalDevice

    def getAttributes(self, path):
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
