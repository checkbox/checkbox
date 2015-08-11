#
# This file is part of Checkbox.
#
# Copyright 2011-2013 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import re
import string

from checkbox_support.lib.bit import get_bitmask
from checkbox_support.lib.bit import test_bit
from checkbox_support.lib.input import Input
from checkbox_support.lib.pci import Pci
from checkbox_support.lib.usb import Usb

PCI_RE = re.compile(
    r"^pci:"
    r"v(?P<vendor_id>[%(hex)s]{8})"
    r"d(?P<product_id>[%(hex)s]{8})"
    r"sv(?P<subvendor_id>[%(hex)s]{8})"
    r"sd(?P<subproduct_id>[%(hex)s]{8})"
    r"bc(?P<class>[%(hex)s]{2})"
    r"sc(?P<subclass>[%(hex)s]{2})"
    r"i(?P<interface>[%(hex)s]{2})"
    % {"hex": string.hexdigits})
PNP_RE = re.compile(
    r"^acpi:"
    r"(?P<vendor_name>[%(upper)s]{3})"
    r"(?P<product_id>[%(hex)s]{4}):"
    % {"upper": string.ascii_uppercase, "hex": string.hexdigits})
USB_RE = re.compile(
    r"^usb:"
    r"v(?P<vendor_id>[%(hex)s]{4})"
    r"p(?P<product_id>[%(hex)s]{4})"
    r"d(?P<revision>[%(hex)s]{4})"
    r"dc(?P<class>[%(hex)s]{2})"
    r"dsc(?P<subclass>[%(hex)s]{2})"
    r"dp(?P<protocol>[%(hex)s]{2})"
    r"ic(?P<interface_class>[%(hex)s]{2})"
    r"isc(?P<interface_subclass>[%(hex)s]{2})"
    r"ip(?P<interface_protocol>[%(hex)s]{2})"
    % {"hex": string.hexdigits})
USB_SYSFS_CONFIG_RE = re.compile(
    r"usb.*?:\d+\.\d+$")
SCSI_RE = re.compile(
    r"^scsi:"
    r"t-0x(?P<type>[%(hex)s]{2})"
    % {"hex": string.hexdigits})
PLATFORM_RE = re.compile(
    r"^platform:"
    r"(?P<module_name>.*)")
INPUT_RE = re.compile(
    r"^input:"
    r"b(?P<bus_type>[%(hex)s]{4})"
    r"v(?P<vendor_id>[%(hex)s]{4})"
    r"p(?P<product_id>[%(hex)s]{4})"
    r"e(?P<version>[%(hex)s]{4})"
    % {"hex": string.hexdigits})
INPUT_SYSFS_ID = re.compile(
    r"/input/input\d+$")
OPENFIRMWARE_RE = re.compile(
    r"^of:"
    r"N(?P<name>.*?)"
    r"T(?P<type>.*?)"
    r"C(?P<compatible>.*?)")
CARD_READER_RE = re.compile(r"SD|MMC|CF|MS(?!ata)|SM|xD|Card", re.I)
GENERIC_RE = re.compile(r"Generic", re.I)
FLASH_RE = re.compile(r"Flash", re.I)
FLASH_DISK_RE = re.compile(r"Mass|Storage|Disk", re.I)


class UdevadmDevice(object):
    __slots__ = (
        "_environment",
        "_name",
        "_bits",
        "_stack",
        "_bus",
        "_interface",
        "_product",
        "_product_id",
        "_vendor",
        "_vendor_id",)

    def __init__(self, environment, name, bits=None, stack=[]):
        self._environment = environment
        self._name = name
        self._bits = bits
        self._stack = stack
        self._bus = None
        self._interface = None
        self._product = None
        self._product_id = None
        self._vendor = None
        self._vendor_id = None

    def __repr__(self):
        vid = int(self.vendor_id) if self.vendor_id else 0
        pid = int(self.product_id) if self.product_id else 0
        return("<{}: bus: {} id [{:x}:{:x}] {}>".format(
            type(self).__name__, self.bus, vid, pid,
            self.product))

    @property
    def name(self):
        if self._name is not None:
            return self._name

    @property
    def bus(self):
        if self._bus is not None:
            return self._bus
        # Change the bus from 'acpi' to 'pnp' for some devices
        if PNP_RE.match(self._environment.get("MODALIAS", "")) \
           and self._raw_path.endswith(":00"):
            return "pnp"

        # Change the bus from 'block' to parent
        if self._environment.get("DEVTYPE") == "disk" and self._stack:
            return self._stack[-1]._environment.get("SUBSYSTEM")

        bus = self._environment.get("SUBSYSTEM")
        if bus == "pnp":
            return None

        if bus == 'input' and any(d.bus == 'usb' for d in self._stack):
            bus = 'usb'

        return bus

    @bus.setter
    def bus(self, value):
        self._bus = value

    @property
    def category(self):
        if "IFINDEX" in self._environment:
            if "DEVTYPE" in self._environment:
                devtype = self._environment["DEVTYPE"]
                if devtype in ("wlan", "wimax"):
                    return "WIRELESS"
            # Ralink and realtek SDIO wireless
            if "INTERFACE" in self._environment:
                if (self.driver and
                    self.driver.startswith('rt') and
                    (self._environment["INTERFACE"].startswith('ra') or
                     self._environment["INTERFACE"].startswith('wlan')
                     )):
                    return "WIRELESS"
            return "NETWORK"

        if self.bus == "bluetooth":
            return "BLUETOOTH"

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
                # Not all DISPLAY devices are display adapters. The ones with
                # subclass OTHER are usually uninteresting devices. As an
                # exception, some vendors have recently begun to use the
                # 0x80 (Pci.CLASS_DISPLAY_OTHER) subclass identifier. In order
                # to correctly identify them special heuristics are needed,
                # these are encapsulated in the known_to_be_video_device method
                # (further below).
                if (subclass_id == Pci.CLASS_DISPLAY_VGA or
                    subclass_id == Pci.CLASS_DISPLAY_3D or
                    (subclass_id == Pci.CLASS_DISPLAY_OTHER
                     and known_to_be_video_device(
                         self.vendor_id, self.product_id, class_id,
                         subclass_id))):
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
            if class_id == Pci.BASE_CLASS_WIRELESS \
               and subclass_id == Pci.CLASS_WIRELESS_BLUETOOTH:
                return "BLUETOOTH"
            if class_id == Pci.BASE_CLASS_BRIDGE \
               and (subclass_id == Pci.CLASS_BRIDGE_PCMCIA
                    or subclass_id == Pci.CLASS_BRIDGE_CARDBUS):
                return "SOCKET"

        if "TYPE" in self._environment and "INTERFACE" in self._environment:
            interface_class, interface_subclass, interface_protocol = (
                int(i) for i in self._environment["INTERFACE"].split("/"))
            if interface_class == Usb.BASE_CLASS_AUDIO:
                return "AUDIO"
            if interface_class == Usb.BASE_CLASS_PRINTER:
                return "PRINTER"
            if interface_class == Usb.BASE_CLASS_STORAGE:
                if interface_subclass == Usb.CLASS_STORAGE_FLOPPY:
                    return "FLOPPY"
                if interface_subclass == Usb.CLASS_STORAGE_SCSI:
                    return "USB"
            if interface_class == Usb.BASE_CLASS_VIDEO:
                return "CAPTURE"
            if interface_class == Usb.BASE_CLASS_WIRELESS:
                if interface_protocol == Usb.PROTOCOL_BLUETOOTH:
                    return "BLUETOOTH"
                else:
                    return "WIRELESS"
            if (interface_class, interface_subclass, interface_protocol) ==\
               (255, 255, 255) and self.driver == "btusb":
                # This heuristic accounts for bluetooth devices which usually
                # have INTERFACE=224/*/1, however in the "field" we've run
                # across a few (Mediatek combo cards) that have unknown
                # (255/255/255) values and thus break the previous heuristic.
                # We assume that if a device has these weird INTERFACE values
                # *but* it uses the btusb driver, then it must be a bluetooth
                # controller.  Other devices with btusb *but* with
                # INTERFACE=255/1/1 have been seen on systems where the actual
                # usb controller was identified by the old heuristic, so here
                # we need to match all three fields to avoid duplicating
                # devices.  See http://pad.lv/1210405
                    return "BLUETOOTH"

        if 'ID_INPUT_KEYBOARD' in self._environment:
            return "KEYBOARD"
        if 'ID_INPUT_TOUCHPAD' in self._environment:
            return "TOUCHPAD"
        if 'ID_INPUT_TOUCHSCREEN' in self._environment:
            return "TOUCHSCREEN"
        if "ID_INPUT_ACCELEROMETER" in self._environment:
            return "ACCELEROMETER"
        if "KEY" in self._environment:
            key = self._environment["KEY"].strip("=")
            bitmask = get_bitmask(key)
            if test_bit(Input.KEY_CAMERA, bitmask, self._bits):
                # Avoid detecting the power button as a capture device
                if self.vendor_id == 0:
                    return "OTHER"
                # Avoid identifying media/hot keys as pure capture devices
                if not (test_bit(Input.KEY_PLAYPAUSE, bitmask, self._bits) or
                        test_bit(Input.KEY_PLAY, bitmask, self._bits) or
                        test_bit(Input.KEY_WLAN, bitmask, self._bits)):
                    # Consider a device with both camera and mouse properties
                    # as a KVM hardware device ("keyboard, video and mouse")
                    if test_bit(Input.BTN_MOUSE, bitmask, self._bits):
                        return "KVM"
                    else:
                        return "CAPTURE"
        if 'ID_INPUT_MOUSE' in self._environment:
            return "MOUSE"

        if self.driver:
            if self.driver.startswith("sdhci"):
                return "CARDREADER"
            if self.driver.startswith("mmc"):
                return "CARDREADER"
            if self.driver == "rts_pstor":
                return "CARDREADER"
            # See http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=702145
            if self.driver.startswith("rtsx"):
                return "CARDREADER"
            if ((self._environment.get("DEVTYPE") not in ("disk", "partition")
                    or 'ID_DRIVE_FLASH_SD' in self._environment
                    or ('ID_MODEL' in self._environment
                        and self._environment['ID_MODEL'] == 'Card_Reader'))
                    and self.driver == "sd" and self.product):
                # The condition:
                #     'ID_MODEL' in self._environment
                #     and
                #     self._environment['ID_MODEL'] == 'Card_Reader'
                # is a workaround specific to LP: #1334224
                # Otherwise, the card reader,
                # 058f:6366 Alcor Micro Corp. Multi Flash Reader,
                # of the system,
                # CID 201009-6503 Dell Inspiron One 2310,
                # will be given the category attribute 'DISK' by udev_resource
                if any(FLASH_RE.search(k) for k in self._environment.keys()):
                    return "CARDREADER"
                if any(d.bus == 'usb' for d in self._stack):
                    if (self.product is not None and
                            CARD_READER_RE.search(self.product)):
                        return "CARDREADER"
                    if (self.vendor is not None and
                            GENERIC_RE.search(self.vendor) and
                            not FLASH_DISK_RE.search(self.product)):
                        return "CARDREADER"

        if "ID_TYPE" in self._environment:
            id_type = self._environment["ID_TYPE"]
            if id_type == "cd":
                return "CDROM"
            if (
                id_type == "disk"
                and not any(d.category == "CARDREADER" for d in self._stack)
            ):
                return "DISK"
            if not any(d.bus == 'usb' for d in self._stack):
                if id_type == "video":
                    return "VIDEO"

        if "DEVTYPE" in self._environment:
            devtype = self._environment["DEVTYPE"]
            if devtype == "disk":
                if "ID_CDROM" in self._environment:
                    return "CDROM"
                if "ID_DRIVE_FLOPPY" in self._environment:
                    return "FLOPPY"
                if self.driver == 'virtio_blk' and self.bus == 'virtio':
                    # A QEMU/KVM virtual disk, but should be treated
                    # as DISK nonetheless
                    return "DISK"
                if self.driver == 'nvme' and self.bus == 'pci':
                    # NVMe device in PCIe bus, this should also be
                    # treated as DISK as it presents block devices
                    # we need to test, and is a valid disk device
                    # we need to report.
                    return "DISK"
            if devtype == "scsi_device":
                match = SCSI_RE.match(self._environment.get("MODALIAS", ""))
                type = int(match.group("type"), 16) if match else -1

                # Check FLASH drives, see /lib/udev/rules.d/80-udisks.rules
                if (
                    type in (0, 7, 14)
                    and not any(d.driver == "rts_pstor" for d in self._stack)
                ):
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

        # Some audio and serial devices have a product but no vendor
        # or product id. Special-case their categories for backwards-
        # compatibility.
        if self.bus == "sound":
            return "AUDIO"

        if self.bus == "tty":
            return "OTHER"

        # Any devices that have a product name and proper vendor and product
        # IDs, but had no other category, are lumped together in OTHER.
        # A few devices may have no self.product but carry PRODUCT data in
        # their environment.
        if ((self.product or self._environment.get("PRODUCT")) and
                None not in (self.vendor_id, self.product_id)):
            return "OTHER"

        # Limbo of devices I couldn't otherwise categorize. In practice
        # having no category means the device may be uninteresting, it's
        # up to downstream users of this class to decide what to do with
        # those devices.
        return None

    @property
    def driver(self):
        if "DRIVER" in self._environment:
            return self._environment["DRIVER"]
        # Check parent device for driver
        if self._stack:
            parent = self._stack[-1]
            if "DRIVER" in parent._environment:
                return parent._environment["DRIVER"]
        return None

    @property
    def path(self):
        devpath = self._environment.get("DEVPATH")
        if (
            (self._environment.get("DEVTYPE") == "disk" and self._stack) or
            "IFINDEX" in self._environment
        ):
            devpath = re.sub(r"/[^/]+/[^/]+$", "", devpath)
        return devpath

    @property
    def _raw_path(self):
        """ Returns the raw device path, this is used internally by
            UdevadmParser only
        """
        return self._environment.get("DEVPATH")

    @property
    def product_id(self):
        if self._product_id is not None:
            return self._product_id
        # pci
        match = PCI_RE.match(self._environment.get("MODALIAS", ""))
        if match:
            return int(match.group("product_id"), 16)
        # usb
        match = USB_RE.match(self._environment.get("MODALIAS", ""))
        if match:
            return int(match.group("product_id"), 16)
        # pnp
        match = PNP_RE.match(self._environment.get("MODALIAS", ""))
        if match:
            product_id = int(match.group("product_id"), 16)
            # Ignore interrupt controllers
            if product_id > 0x0100:
                return product_id
        # input
        match = INPUT_RE.match(self._environment.get("MODALIAS", ""))
        if match:
            return int(match.group("product_id"), 16)
        return None

    @product_id.setter
    def product_id(self, value):
        self._product_id = value

    @property
    def vendor_id(self):
        if self._vendor_id is not None:
            return self._vendor_id
        # pci
        match = PCI_RE.match(self._environment.get("MODALIAS", ""))
        if match:
            return int(match.group("vendor_id"), 16)
        # usb
        match = USB_RE.match(self._environment.get("MODALIAS", ""))
        if match:
            return int(match.group("vendor_id"), 16)
        # input
        match = INPUT_RE.match(self._environment.get("MODALIAS", ""))
        if match:
            vendor_id = int(match.group("vendor_id"), 16)
            # Vendor id <= 9 are not valid numbers, force 9 to make sure
            # that it will not match an existing (unrelated) vendor in usb.ids
            # nor pci.ids
            if vendor_id and vendor_id < 9:
                vendor_id = 9
            return vendor_id
        return None

    @vendor_id.setter
    def vendor_id(self, value):
        self._vendor_id = value

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
        if self._product is not None:
            return self._product
        # disk
        if self._environment.get("DEVTYPE") == "scsi_device":
            for device in reversed(self._stack):
                if device._environment.get("ID_BUS") == "usb":
                    return decode_id(device._environment["ID_MODEL_ENC"])
        elif (self._environment.get("DEVTYPE") == "disk" and
                "ID_MODEL_ENC" in self._environment):
            return decode_id(self._environment["ID_MODEL_ENC"])

        # floppy
        if self.driver == "floppy":
            return "Platform Device"

        if "ID_MODEL_FROM_DATABASE" in self._environment:
            return self._environment["ID_MODEL_FROM_DATABASE"]

        # bluetooth (if USB base class is vendor specific)
        if self.bus == 'bluetooth':
            vendor_specific = False
            # Check parent device modalias
            if self._stack:
                parent = self._stack[-1]
                if "MODALIAS" in parent._environment:
                    match = USB_RE.match(
                        parent._environment.get("MODALIAS", ""))
                    if match:
                        if int(match.group("class"), 16) == 0xFF:
                            vendor_specific = True
            if vendor_specific:
                for device in reversed(self._stack):
                    if "ID_MODEL_ENC" in device._environment:
                        return decode_id(device._environment["ID_MODEL_ENC"])

        if "IFINDEX" in self._environment:
            for device in reversed(self._stack):
                # wireless (SoC)
                match = PLATFORM_RE.match(
                    device._environment.get("MODALIAS", ""))
                if match:
                    return match.group("module_name")
                # Network (Open Firmware)
                match = OPENFIRMWARE_RE.match(
                    device._environment.get("MODALIAS", ""))
                if match:
                    return match.group("name")

        if "IFINDEX" in self._environment and "INTERFACE" in self._environment:
            if "ID_MODEL_ENC" in self._environment:
                return decode_id(self._environment["ID_MODEL_ENC"])

        for element in ("NAME", "POWER_SUPPLY_MODEL_NAME"):
            if element in self._environment:
                return self._environment[element].strip('"')

        return None

    @product.setter
    def product(self, value):
        self._product = value

    @property
    def vendor(self):
        if self._vendor is not None:
            return self._vendor
        if "RFKILL_NAME" in self._environment:
            return None

        if "POWER_SUPPLY_MANUFACTURER" in self._environment:
            return self._environment["POWER_SUPPLY_MANUFACTURER"]

        # pnp
        match = PNP_RE.match(self._environment.get("MODALIAS", ""))
        if match:
            return match.group("vendor_name")

        # disk
        if self._environment.get("DEVTYPE") == "scsi_device":
            for device in reversed(self._stack):
                if device._environment.get("ID_BUS") == "usb":
                    return decode_id(device._environment["ID_VENDOR_ENC"])
        elif (self._environment.get("DEVTYPE") == "disk" and
                "ID_VENDOR_ENC" in self._environment):
            return decode_id(self._environment["ID_VENDOR_ENC"])

        if "ID_VENDOR_FROM_DATABASE" in self._environment:
            return self._environment["ID_VENDOR_FROM_DATABASE"]

        # bluetooth (if USB base class is vendor specific)
        if self.bus == 'bluetooth':
            vendor_specific = False
            # Check parent device modalias
            if self._stack:
                parent = self._stack[-1]
                if "MODALIAS" in parent._environment:
                    match = USB_RE.match(
                        parent._environment.get("MODALIAS", ""))
                    if match:
                        if int(match.group("class"), 16) == 0xFF:
                            vendor_specific = True
            if vendor_specific:
                for device in reversed(self._stack):
                    if "ID_VENDOR_ENC" in device._environment:
                        return decode_id(device._environment["ID_VENDOR_ENC"])

        if "IFINDEX" in self._environment and "INTERFACE" in self._environment:
            if "ID_VENDOR_ENC" in self._environment:
                return decode_id(self._environment["ID_VENDOR_ENC"])

        return None

    @vendor.setter
    def vendor(self, value):
        self._vendor = value

    @property
    def interface(self):
        if self._interface is not None:
            return self._interface
        if (self.category in ("NETWORK", "WIRELESS") and
                "INTERFACE" in self._environment):
            return self._environment["INTERFACE"]
        return None

    @interface.setter
    def interface(self, value):
        self._interface = value

    def as_json(self):
        attributes = ("path", "bus", "category", "driver", "product_id",
                      "vendor_id", "subproduct_id", "subvendor_id", "product",
                      "vendor", "interface", "name")

        return {a: getattr(self, a) for a in attributes if getattr(self, a)}


class UdevadmParser(object):
    """Parser for the udevadm command."""

    device_factory = UdevadmDevice

    def __init__(self, stream_or_string, bits=None):
        self.stream_or_string = stream_or_string
        self.bits = bits
        self.devices = OrderedDict()

    def _ignoreDevice(self, device):
        # Ignore devices without bus information
        if not device.bus:
            return True

        # Do not ignore devices with bus == net and ID_NET_NAME_MAC
        # These can be virtual network interfaces which don't have PCI
        # product/vendor ID, yet still constitute valid ethX interfaces.
        if device.bus == "net" and "ID_NET_NAME_MAC" in device._environment:
            return False
        # Do not ignore nvme devices on the pci bus, these are to be treated
        # as disks (categorization is done elsewhere). Note that the *parent*
        # device will have no category, though it's not ignored per se.
        if device.bus == 'pci' and device.driver == 'nvme':
            return False

        # Do not ignore QEMU/KVM virtio disks
        if ("ID_PART_TABLE_TYPE" in device._environment and
           device.bus == "virtio" and
           device.driver == "virtio_blk"):
            return False

        # Ignore devices without product AND vendor information
        if (device.product is None and device.product_id is None and
                device.vendor is None and device.vendor_id is None):
            return True

        # Ignore invalid subsystem information
        if (
            (device.subproduct_id is None
                and device.subvendor_id is not None)
            or (device.subproduct_id is not None
                and device.subvendor_id is None)):
            return True

        # Ignore ACPI devices
        if device.bus == "acpi":
            return True

        return False

    def getAttributes(self, path):
        return {}

    def run(self, result):
        # Some attribute lines have a space character after the
        # ':', others don't have it (see udevadm-info.c).
        line_pattern = re.compile(r"(?P<key>[A-Z]):\s*(?P<value>.*)")
        multi_pattern = re.compile(r"(?P<key>[^=]+)=(?P<value>.*)")

        stack = []
        if isinstance(self.stream_or_string, type("")):
            output = self.stream_or_string
        else:
            output = self.stream_or_string.read()
        output = output.replace('\r', '')  # Just in case...
        for record in re.split("\n{2,}", output):
            record = record.strip()
            if not record:
                continue

            # Determine path, name and environment
            path = None
            name = None
            element = None
            environment = {}
            for line in record.splitlines():
                line_match = line_pattern.match(line)
                if not line_match:
                    if environment:
                        # Append to last environment element
                        environment[element] += line
                    continue

                key = line_match.group("key")
                value = line_match.group("value")

                if key == "P":
                    path = value
                elif key == "N":
                    name = value
                elif key == "E":
                    key_match = multi_pattern.match(value)
                    if not key_match:
                        raise Exception(
                            "Device property not supported: %s" % value)
                    element = key_match.group("key")
                    environment[element] = key_match.group("value")

            # Update stack
            while stack:
                if stack[-1]._raw_path + "/" in path:
                    break
                stack.pop()

            # Set default DEVPATH
            environment.setdefault("DEVPATH", path)

            device = self.device_factory(
                environment, name, self.bits, list(stack))
            if not self._ignoreDevice(device):
                if device._raw_path in self.devices:
                    if self.devices[device._raw_path].category == 'CARDREADER':
                        [
                            setattr(self.devices[device._raw_path],
                                    device_key, getattr(device, device_key))
                            for device_key in (
                                "product", "vendor", "product_id", "vendor_id")
                            if getattr(device, device_key) is not None
                        ]
                    elif device.category != "OTHER":
                        self.devices[device._raw_path] = device
                elif device.category == 'BLUETOOTH':
                    usb_interface_path = USB_SYSFS_CONFIG_RE.sub(
                        '', device._raw_path)
                    if not [
                        d for d in self.devices.values()
                        if d.category == 'BLUETOOTH' and
                        usb_interface_path in d._raw_path
                    ]:
                        self.devices[device._raw_path] = device
                elif device.category == 'CAPTURE':
                    input_id = INPUT_SYSFS_ID.sub('', device._raw_path)
                    if [
                        d for d in self.devices.values()
                        if d.category == 'CAPTURE' and input_id in d._raw_path
                    ]:
                        self.devices[input_id].product = device.product
                    else:
                        usb_interface_path = USB_SYSFS_CONFIG_RE.sub(
                            '', device._raw_path)
                        if not [
                            d for d in self.devices.values()
                            if d.category == 'CAPTURE' and
                            usb_interface_path in d._raw_path
                        ]:
                            self.devices[device._raw_path] = device
                else:
                    self.devices[device._raw_path] = device
            stack.append(device)

        for device in list(self.devices.values()):
            if device.category in ("NETWORK", "WIRELESS", "OTHER"):
                dev_interface = [
                    d for d in self.devices.values()
                    if d.category in ("NETWORK", "WIRELESS") and
                    device._raw_path != d._raw_path and
                    device._raw_path in d._raw_path
                ]
                if dev_interface:
                    dev_interface = dev_interface.pop()
                    dev_interface.bus = device.bus
                    dev_interface.product_id = device.product_id
                    dev_interface.vendor_id = device.vendor_id
                    self.devices.pop(device._raw_path, None)

        [result.addDevice(device) for device in self.devices.values()]


def decode_id(id):
    encoded_id = id.encode("utf-8")
    decoded_id = encoded_id.decode("unicode-escape")
    return decoded_id.strip()


def known_to_be_video_device(vendor_id, product_id, pci_class, pci_subclass):
    # Usually a video device has a PCI subclass_id of Pci.CLASS_DISPLAY_VGA or
    # Pci.CLASS_DISPLAY_3d. However, some manufacturers which hadn't previously
    # used a subclass_id of Pci.CLASS_DISPLAY_OTHER (0x80 or decimal 128) have
    # begun to do so (as of 2013-2014); and others which previously used this
    # class for uninteresting devices are now using it for actual video
    # devices. This method encapsulates heuristics to decide if a device is a
    # valid video adapter, based on product/vendor and pci class/subclass
    # information.
    if vendor_id == Pci.VENDOR_ID_AMD:
        # AMD hadn't used subclass OTHER before, so all AMD devices we get
        # asked about are VIDEO.
        return True
    if vendor_id == Pci.VENDOR_ID_INTEL:
        # Intel recently (2014) started using subclass OTHER erratically, some
        # older GPUs have subdevices with OTHER which are uninteresting. If
        # Intel, we only consider OTHER devices as VIDEO if they are in this
        # explicit list
        return product_id in [0x0152, 0x0412, 0x0402]


class UdevResult(object):
    def __init__(self):
        self.devices = {"device_list": []}

    def addDevice(self, device):
        self.devices["device_list"].append(device)


def parse_udevadm_output(output, bits=None):
    """
    Parse output of `LANG=C udevadm info --export-db`

    :returns: :class:`UdevadmParser` object that corresponds to the
    parsed input
    """
    udev = UdevadmParser(output, bits)
    result = UdevResult()
    udev.run(result)
    return result.devices
