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

from checkbox.lib.cache import cache

from checkbox.properties import String
from checkbox.registry import Registry
from checkbox.registries.command import CommandRegistry
from checkbox.registries.link import LinkRegistry
from checkbox.registries.map import MapRegistry
from checkbox.registries.none import NoneRegistry


USB_IDS = "/usr/share/misc/usb.ids"
PCI_IDS = "/usr/share/misc/pci.ids"

PCI_BASE_CLASS_STORAGE =        1
PCI_CLASS_STORAGE_SCSI =        0
PCI_CLASS_STORAGE_IDE =         1
PCI_CLASS_STORAGE_FLOPPY =      2
PCI_CLASS_STORAGE_IPI =         3
PCI_CLASS_STORAGE_RAID =        4
PCI_CLASS_STORAGE_OTHER =       80

PCI_BASE_CLASS_NETWORK =        2
PCI_CLASS_NETWORK_ETHERNET =    0
PCI_CLASS_NETWORK_TOKEN_RING =  1
PCI_CLASS_NETWORK_FDDI =        2
PCI_CLASS_NETWORK_ATM =         3
PCI_CLASS_NETWORK_OTHER =       80
PCI_CLASS_NETWORK_WIRELESS =    128

PCI_BASE_CLASS_DISPLAY =        3
PCI_CLASS_DISPLAY_VGA =         0
PCI_CLASS_DISPLAY_XGA =         1
PCI_CLASS_DISPLAY_3D =          2
PCI_CLASS_DISPLAY_OTHER =       80

PCI_BASE_CLASS_MULTIMEDIA =     4
PCI_CLASS_MULTIMEDIA_VIDEO =    0
PCI_CLASS_MULTIMEDIA_AUDIO =    1
PCI_CLASS_MULTIMEDIA_PHONE =    2
PCI_CLASS_MULTIMEDIA_OTHER =    80

PCI_BASE_CLASS_BRIDGE =         6
PCI_CLASS_BRIDGE_HOST =         0
PCI_CLASS_BRIDGE_ISA =          1
PCI_CLASS_BRIDGE_EISA =         2
PCI_CLASS_BRIDGE_MC =           3
PCI_CLASS_BRIDGE_PCI =          4
PCI_CLASS_BRIDGE_PCMCIA =       5
PCI_CLASS_BRIDGE_NUBUS =        6
PCI_CLASS_BRIDGE_CARDBUS =      7
PCI_CLASS_BRIDGE_RACEWAY =      8
PCI_CLASS_BRIDGE_OTHER =        80

PCI_BASE_CLASS_COMMUNICATION =  7
PCI_CLASS_COMMUNICATION_SERIAL = 0
PCI_CLASS_COMMUNICATION_PARALLEL = 1
PCI_CLASS_COMMUNICATION_MULTISERIAL = 2
PCI_CLASS_COMMUNICATION_MODEM = 3
PCI_CLASS_COMMUNICATION_OTHER = 80

PCI_BASE_CLASS_INPUT =          9
PCI_CLASS_INPUT_KEYBOARD =      0
PCI_CLASS_INPUT_PEN =           1
PCI_CLASS_INPUT_MOUSE =         2
PCI_CLASS_INPUT_SCANNER =       3
PCI_CLASS_INPUT_GAMEPORT =      4
PCI_CLASS_INPUT_OTHER =         80

PCI_BASE_CLASS_SERIAL =         12
PCI_CLASS_SERIAL_FIREWIRE =     0
PCI_CLASS_SERIAL_ACCESS =       1

PCI_CLASS_SERIAL_SSA =          2
PCI_CLASS_SERIAL_USB =          3
PCI_CLASS_SERIAL_FIBER =        4
PCI_CLASS_SERIAL_SMBUS =        5


class DeviceRegistry(Registry):

    def __init__(self, parent, environment, attributes):
        super(DeviceRegistry, self).__init__()
        self._parent = parent
        self._environment = environment
        self._attributes = attributes

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self.items()
            if not isinstance(v, Registry)]

        return "\n".join(strings)

    @cache
    def _load_ids(cls, filename):
        vendor_re = re.compile(r"^(?P<id>[%s]{4})\s+(?P<name>.*\S)\s*$"
            % string.hexdigits)
        device_re = re.compile(r"^\t(?P<id>[%s]{4})\s+(?P<name>.*\S)\s*$"
            % string.hexdigits)

        ids = {}
        file = open(filename, "r")
        for line in file.readlines():
            match = vendor_re.match(line)
            if match:
                vendor_id = int(match.group("id"), 16)
                vendor_name = match.group("name").strip()
                ids[vendor_id] = {"name": vendor_name}
            else:
                match = device_re.match(line)
                if match:
                    device_id = int(match.group("id"), 16)
                    device_name = match.group("name").strip()
                    ids[vendor_id].setdefault("devices", {})
                    ids[vendor_id]["devices"][device_id] = {"name": device_name}

        return ids

    def _get_ids(self):
        bus = self._get_bus()
        if bus == "pci":
            return DeviceRegistry._load_ids(PCI_IDS)
        elif bus == "usb":
            return DeviceRegistry._load_ids(USB_IDS)
        else:
            return None
        
    def _get_bus(self):
        if "MODALIAS" in self._environment:
            return self._environment["MODALIAS"].split(":")[0]
        elif "ID_BUS" in self._environment:
            return self._environment["ID_BUS"]
        elif "DEVPATH" in self._environment:
            devpath = self._environment["DEVPATH"]
            if devpath.startswith("/devices/pnp"):
                return "pnp"
            elif "power_supply" in devpath.split("/"):
                return "power_supply"
            elif "rfkill" in devpath.split("/"):
                return "rfkill"

        return "Unknown"

    def _get_category(self):
        if "IFINDEX" in self._environment:
            return "NETWORK"

        if "PCI_CLASS" in self._environment:
            pci_class = self._environment["PCI_CLASS"]
            prog_if = int(pci_class[-2:], 16)
            subclass_id = int(pci_class[-4:-2], 16)
            class_id = int(pci_class[:-4], 16)

            if class_id == PCI_BASE_CLASS_NETWORK:
                return "NETWORK"

            if class_id == PCI_BASE_CLASS_DISPLAY:
                return "VIDEO"

            if class_id == PCI_BASE_CLASS_SERIAL \
               and subclass_id == PCI_CLASS_SERIAL_USB:
                return "USB"

            if class_id == PCI_BASE_CLASS_STORAGE:
                if subclass_id == PCI_CLASS_STORAGE_SCSI:
                    return "SCSI"

                if subclass_id == PCI_CLASS_STORAGE_IDE:
                    return "IDE"

                if subclass_id == PCI_CLASS_STORAGE_FLOPPY:
                    return "FLOPPY"

                if subclass_id == PCI_CLASS_STORAGE_RAID:
                    return "RAID"

            if class_id == PCI_BASE_CLASS_COMMUNICATION \
               and subclass_id == PCI_CLASS_COMMUNICATION_MODEM:
                return "MODEM"

            if class_id == PCI_BASE_CLASS_INPUT \
               and subclass_id == PCI_CLASS_INPUT_SCANNER:
                return "SCANNER"

            if class_id == PCI_BASE_CLASS_MULTIMEDIA:
                if subclass_id == PCI_CLASS_MULTIMEDIA_VIDEO:
                    return "CAPTURE"

                if subclass_id == PCI_CLASS_MULTIMEDIA_AUDIO:
                    return "AUDIO"

            if class_id == PCI_BASE_CLASS_SERIAL \
               and subclass_id == PCI_CLASS_SERIAL_FIREWIRE:
                return "FIREWIRE"

            if class_id == PCI_BASE_CLASS_BRIDGE \
               and (subclass_id == PCI_CLASS_BRIDGE_PCMCIA \
                    or subclass_id == PCI_CLASS_BRIDGE_CARDBUS):
                return "SOCKET"

        if "ID_TYPE" in self._environment:
            id_type = self._environment["ID_TYPE"]

            if id_type == "cd":
                return "CDROM"

            if id_type == "disk":
                return "DISK"

            if id_type == "video":
                return "VIDEO"

        if "MODALIAS" in self._environment:
            bus = self._environment["MODALIAS"].split(":")[0]
            if bus == "input":
                if "keyboard" in self._environment.get("NAME", "").lower():
                    return "KEYBOARD"
                if "mouse" in self._environment.get("NAME", "").lower():
                    return "MOUSE"

        if self._environment.get("DEVTYPE") == "disk":
            if "ID_CDROM" in self._environment:
                return "CDROM"

            if "ID_DRIVE_FLOPPY" in self._environment:
                return "FLOPPY"

        if "PCI_ID" in self._environment or "ID_MODEL_ID" in self._environment:
            return "OTHER"

        return None

    def _get_driver(self):
        if "DRIVER" in self._environment:
            return self._environment["DRIVER"]
        elif "ID_USB_DRIVER" in self._environment:
            return self._environment["ID_USB_DRIVER"]

        return "Unknown"

    def _get_path(self):
        return self._environment["DEVPATH"]

    def _get_type(self):
        if "TYPE" in self._environment:
            return self._environment["TYPE"]
        if "ID_TYPE" in self._environment:
            return self._environment["ID_TYPE"]
        elif "type" in self._attributes:
            return self._attributes["type"]
        elif "chassis_type" in self._attributes:
            return self._attributes["chassis_type"]

        return None

    def _get_vendor_id(self):
        if "PCI_ID" in self._environment:
            vendor_id, product_id = self._environment["PCI_ID"].split(":")
            return int(vendor_id, 16)
        elif "ID_VENDOR_ID" in self._environment:
            return int(self._environment["ID_VENDOR_ID"], 16)
        elif "idVendor" in self._attributes:
            return int(self._attributes["idVendor"], 16)
        else:
            bus = self._get_bus()
            if bus == "usb" and "PRODUCT" in self._environment:
                product = self._environment["PRODUCT"]
                vendor_id, product_id, revision_bcd = product.split("/")
                return int(vendor_id, 16)

        return None

    def _get_product_id(self):
        if "PCI_ID" in self._environment:
            vendor_id, product_id = self._environment["PCI_ID"].split(":")
            return int(product_id, 16)
        elif "ID_MODEL_ID" in self._environment:
            return int(self._environment["ID_MODEL_ID"], 16)
        elif "idProduct" in self._attributes:
            return int(self._attributes["idProduct"], 16)
        else:
            bus = self._get_bus()
            if bus == "usb" and "PRODUCT" in self._environment:
                product = self._environment["PRODUCT"]
                vendor_id, product_id, revision_bcd = product.split("/")
                return int(product_id, 16)

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

    def _get_vendor_by_id(self, vendor_id):
        ids = self._get_ids()
        if ids \
           and vendor_id in ids:
            return ids[vendor_id]["name"]

        return "Unknown"

    def _get_vendor(self):
        if "ID_VENDOR_ENC" in self._environment:
            id_vendor_enc = self._environment["ID_VENDOR_ENC"]
            return id_vendor_enc.decode("string_escape").strip()
        elif "POWER_SUPPLY_MANUFACTURER" in self._environment:
            return self._environment["POWER_SUPPLY_MANUFACTURER"]
        elif "board_vendor" in self._attributes:
            return self._attributes["board_vendor"]
        elif "vendor" in self._attributes:
            vendor = self._attributes["vendor"]
            if re.match(r"^0x[%s]{4}$" % string.hexdigits, vendor):
                vendor_id = int(vendor, 16)
                return self._get_vendor_by_id(vendor_id)
            else:
                return vendor
        elif "vendor" in self._parent:
            return self._parent["vendor"]
        else:
            vendor_id = self._get_vendor_id()
            return self._get_vendor_by_id(vendor_id)

    def _get_model_by_vendor_and_product_id(self, vendor_id, product_id):
        ids = self._get_ids()
        if ids \
           and vendor_id in ids \
           and product_id in ids[vendor_id]["devices"]:
            return ids[vendor_id]["devices"][product_id]["name"]

        return "Unknown"

    def _get_model(self):
        if "NAME" in self._environment:
            return self._environment["NAME"].strip('"')
        elif "ID_MODEL_ENC" in self._environment:
            id_model_enc = self._environment["ID_MODEL_ENC"]
            return id_model_enc.decode("string_escape").strip()
        elif "POWER_SUPPLY_MODEL_NAME" in self._environment:
            return self._environment["POWER_SUPPLY_MODEL_NAME"]
        elif "RFKILL_NAME" in self._environment:
            return self._environment["RFKILL_NAME"]
        elif "platform" in self._environment["DEVPATH"]:
            name = self._environment["DEVPATH"].split("/")[-1]
            return "Platform Device (%s)" % name
        elif "board_name" in self._attributes:
            return self._attributes["board_name"]
        elif "description" in self._attributes:
            return self._attributes["description"]
        elif "model" in self._attributes:
            return self._attributes["model"]
        elif "id" in self._attributes:
            return self._attributes["id"]
        else:
            vendor_id = self._get_vendor_id()
            product_id = self._get_product_id()
            return self._get_model_by_vendor_and_product_id(vendor_id,
                product_id)

    def items(self):
        return (
            ("category", self._get_category()),
            ("bus", self._get_bus()),
            ("driver", self._get_driver()),
            ("path", self._get_path()),
            ("vendor_id", self._get_vendor_id()),
            ("product_id", self._get_product_id()),
            ("subvendor_id", self._get_subvendor_id()),
            ("subproduct_id", self._get_subproduct_id()),
            ("vendor", self._get_vendor()),
            ("model", self._get_model()),
            ("type", self._get_type()),
            ("attributes", MapRegistry(self._attributes)),
            ("device", LinkRegistry(self)))


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

            if [c for c in value if not isprint(c)]:
                continue

            attributes[name] = value

        return attributes

    def _ignore_device(self, device):
        if device.bus in ("Unknown", "acpi"):
            return True

        if device.bus == "usb" \
           and (device.category == None \
                or device.driver == "hub"):
            return True

        if device.bus == "pnp" \
           and (device.driver in ("Unknown", "system")):
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

            # Determine parent
            parent = NoneRegistry()
            for parent_path, parent_device in reversed(items):
                if path.startswith(parent_path):
                    parent = parent_device
                    break

            # Determine attributes
            attributes = self._get_attributes(path)

            device = DeviceRegistry(parent, environment, attributes)
            if not self._ignore_device(device):
                items.append((path, device))

        return items


factory = UdevRegistry
