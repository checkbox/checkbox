#
# This file is part of Checkbox.
#
# Copyright 2012-2013 Canonical Ltd.
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
from io import StringIO

from pkg_resources import resource_filename
from unittest import TestCase

from checkbox.parsers.udevadm import UdevadmParser, decode_id
from checkbox.parsers.udevadm import parse_udevadm_output


class DeviceResult:

    def __init__(self):
        self.devices = []

    def addDevice(self, device):
        self.devices.append(device)

    def getDevice(self, category):
        for device in self.devices:
            if device.category == category:
                return device

        return None


class UdevadmDataMixIn:
    """
    Mix in with a helper method to load sample udevadm data
    """

    def get_text(self, name):
        resource = 'parsers/tests/udevadm_data/{}.txt'.format(name)
        filename = resource_filename('checkbox', resource)
        with open(filename, 'rt', encoding='UTF-8') as stream:
            return stream.read()


class TestUdevadmParser(TestCase, UdevadmDataMixIn):

    def getParser(self, string):
        stream = StringIO(string)
        return UdevadmParser(stream)

    def getResult(self, string):
        parser = self.getParser(string)
        result = DeviceResult()
        parser.run(result)
        return result

    def parse(self, name):
        # Uncomment only for debugging purpose
        #attributes = ("path", "driver", "bus", "product_id", "vendor_id",
        #    "product", "vendor", "interface",)
        #
        #devices = parse_udevadm_output(self.get_text(name), 64)["device_list"]
        #for i,j in enumerate(devices):
            #print(i, j.category, [getattr(j, a) for a in attributes])
        return parse_udevadm_output(self.get_text(name), 64)["device_list"]

    def count(self, devices, category):
        return len([d for d in devices if d.category == category])

    def test_usb_capture(self):
        result = self.getResult("""
P: /devices/pci0000:00/0000:00:1a.7/usb1/1-6/1-6:1.0
E: UDEV_LOG=3
E: DEVPATH=/devices/pci0000:00/0000:00:1a.7/usb1/1-6/1-6:1.0
E: DEVTYPE=usb_interface
E: DRIVER=uvcvideo
E: PRODUCT=17ef/480c/3134
E: TYPE=239/2/1
E: INTERFACE=14/1/0
E: MODALIAS=usb:v17EFp480Cd3134dcEFdsc02dp01ic0Eisc01ip00
E: SUBSYSTEM=usb
""")
        device = result.getDevice("CAPTURE")
        self.assertTrue(device)

    def test_openfirmware_network(self):
        result = self.getResult("""
P: /devices/soc.0/ffe64000.ethernet
E: DEVPATH=/devices/soc.0/ffe64000.ethernet
E: DRIVER=XXXXX
E: MODALIAS=of:NethernetTXXXXXCXXXXX,XXXXX
E: OF_COMPATIBLE_0=XXXXX,XXXXX
E: OF_COMPATIBLE_N=1
E: OF_NAME=ethernet
E: OF_TYPE=XXXXX
E: SUBSYSTEM=platform
E: UDEV_LOG=3

P: /devices/soc.0/ffe64000.ethernet/net/eth1
E: DEVPATH=/devices/soc.0/ffe64000.ethernet/net/eth1
E: IFINDEX=3
E: INTERFACE=eth1
E: SUBSYSTEM=net
E: UDEV_LOG=3
""")
        device = result.getDevice("NETWORK")
        self.assertTrue(device)

    def _test_DELL_INSPIRON3521_TOUCHSCREEN(self):
        """
        Check devices category having the ID_INPUT_TOUCHSCREEN property
        """
        devices = self.parse("DELL_INSPIRON3521_TOUCHSCREEN")
        self.assertEqual(len(devices), 59)
        # Check the Accelerometer device category/product
        self.assertEqual(devices[36].category, "TOUCHSCREEN")
        self.assertEqual(devices[36].product, "ELAN Touchscreen")
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 0)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 1)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "DISK"), 2)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "CAPTURE"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)

    def test_DELL_LATITUDEE4310(self):
        devices = self.parse("DELL_LATITUDEE4310")
        self.assertEqual(len(devices), 73)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "CAPTURE"), 0)
        self.assertEqual(self.count(devices, "RAID"), 1)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 0)
        self.assertEqual(self.count(devices, "DISK"), 2)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)

    def test_DELL_LATITUDEE6430(self):
        devices = self.parse("DELL_LATITUDEE6430")
        self.assertEqual(len(devices), 76)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 0)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 2)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "RAID"), 1)
        self.assertEqual(self.count(devices, "DISK"), 2)
        # Check that a Bluetooth device is properly detected
        # See https://bugs.launchpad.net/checkbox/+bug/1075052
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.assertEqual(self.count(devices, "CAPTURE"), 1)

    def test_DELL_OPTIPLEX9020AIO(self):
        devices = self.parse("DELL_OPTIPLEX9020AIO")
        self.assertEqual(len(devices), 60)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 2)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 0)
        self.assertEqual(self.count(devices, "CARDREADER"), 3)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "CAPTURE"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 0)
        self.assertEqual(self.count(devices, "RAID"), 1)
        # At least one network device must be detected to solve
        # https://bugs.launchpad.net/checkbox/+bug/1167733
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.assertEqual(self.count(devices, "DISK"), 2)

    def test_DELL_VOSTRO3460_FINGERPRINT(self):
        """
        This system has a fingerprint reader

        usb.ids:
        138a  Validity Sensors, Inc.
                0011  VFS5011 Fingerprint Reader
        """
        devices = self.parse("DELL_VOSTRO3460_FINGERPRINT")
        self.assertEqual(len(devices), 73)
        self.assertEqual(devices[35].category, "OTHER")
        self.assertEqual(devices[35].vendor_id, 0x0138a)
        self.assertEqual(devices[35].product_id, 0x0011)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 0)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "DISK"), 1)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 2)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.assertEqual(self.count(devices, "CAPTURE"), 1)

    def test_DELL_VOSTROV131(self):
        devices = self.parse("DELL_VOSTROV131")
        expected_devices = {"RTL8111/8168 PCI Express Gigabit "
                            "Ethernet controller":
                            ("NETWORK", "pci", 0x10EC, 0x8168),
                            "AR9285 Wireless Network Adapter (PCI-Express)":
                            ("WIRELESS", "pci", 0x168C, 0x002B)
                            }
        self.assertEqual(len(devices), 60)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 0)
        self.assertEqual(self.count(devices, "CDROM"), 0)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 0)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "DISK"), 2)
        self.assertEqual(self.count(devices, "CAPTURE"), 1)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 2)
        self.verify_devices(devices, expected_devices)

    def test_DELL_XPS1340(self):
        devices = self.parse("DELL_XPS1340")
        self.assertEqual(len(devices), 75)
        self.assertEqual(self.count(devices, "VIDEO"), 2)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 3)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 1)
        self.assertEqual(self.count(devices, "MOUSE"), 0)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "DISK"), 1)
        self.assertEqual(self.count(devices, "CAPTURE"), 0)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)

    def test_HOME_MADE(self):
        devices = self.parse("HOME_MADE")
        self.assertEqual(len(devices), 69)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 2)
        self.assertEqual(self.count(devices, "KEYBOARD"), 2)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 0)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 2)
        self.assertEqual(self.count(devices, "FLOPPY"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 1)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "CAPTURE"), 0)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 0)
        self.assertEqual(self.count(devices, "WIRELESS"), 0)
        self.assertEqual(self.count(devices, "DISK"), 2)
        self.assertEqual(self.count(devices, "NETWORK"), 1)

    def test_HP_PAVILIONSLEEKBOOK14_ACCELEROMETER(self):
        devices = self.parse("HP_PAVILIONSLEEKBOOK14_ACCELEROMETER")
        self.assertEqual(len(devices), 56)
        self.assertEqual(devices[54].product, "ST LIS3LV02DL Accelerometer")
        self.assertEqual(devices[54].category, "ACCELEROMETER")
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 0)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 0)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 1)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "CAPTURE"), 0)
        # Check that a Bluetooth device is properly detected on PCI bus
        # See https://bugs.launchpad.net/checkbox/+bug/1036124
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "DISK"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)

    def test_HP_PRO2110(self):
        devices = self.parse("HP_PRO2110")
        self.assertEqual(len(devices), 54)
        # Check that the Avocent IBM 73P5832 is not a CAPTURE device
        # See https://bugs.launchpad.net/checkbox/+bug/1065064
        self.assertEqual(devices[32].product, "Avocent IBM 73P5832")
        self.assertNotEqual(devices[32].category, "CAPTURE")
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 0)
        self.assertEqual(self.count(devices, "CARDREADER"), 4)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "CAPTURE"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 0)
        self.assertEqual(self.count(devices, "WIRELESS"), 0)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "DISK"), 2)
        self.assertEqual(self.count(devices, "NETWORK"), 1)

    def test_HP_PROBOOK6550B_ACCELEROMETER(self):
        devices = self.parse("HP_PROBOOK6550B_ACCELEROMETER")
        expected_devices = {"Centrino Advanced-N 6200":
                            ("WIRELESS", "pci", 0x8086, 0x4239),
                            "82577LC Gigabit Network Connection":
                            ("NETWORK", "pci", 0x8086, 0x10EB)
                            }
        self.assertEqual(len(devices), 78)
        # Check the accelerometer device category/product
        self.assertEqual(devices[76].product, "ST LIS3LV02DL Accelerometer")
        self.assertEqual(devices[76].category, "ACCELEROMETER")
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 1)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 1)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "DISK"), 2)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "CAPTURE"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.verify_devices(devices, expected_devices)

    def test_LENOVO_E431(self):
        devices = self.parse("LENOVO_E431")
        self.assertEqual(len(devices), 63)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "DISK"), 1)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "CAPTURE"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)

    def test_LENOVO_E445(self):
        devices = self.parse("LENOVO_E445")
        self.assertEqual(len(devices), 76)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 2)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "DISK"), 1)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "CAPTURE"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)

    def test_LENOVO_T430S(self):
        devices = self.parse("LENOVO_T430S")
        expected_devices = {"Centrino Ultimate-N 6300":
                            ("WIRELESS", "pci", 0x8086, 0x4238),
                            "82579LM Gigabit Network Connection":
                            ("NETWORK", "pci", 0x8086, 0x1502),
                            "H5321 gw":
                            ("NETWORK", "usb", 0x0bdb, 0x1926)
                            }
        self.assertEqual(len(devices), 102)
        # Check that the Thinkpad hotkeys are not a CAPTURE device
        self.assertEqual(devices[101].product, "ThinkPad Extra Buttons")
        self.assertEqual(devices[101].category, "OTHER")
        # Check that the Ericsson MBM module is set as a NETWORK device with
        # proper vendor/product names
        self.assertEqual(devices[54].product, "H5321 gw")
        self.assertEqual(
            devices[54].vendor,
            "Ericsson Business Mobile Networks BV")
        self.assertEqual(devices[54].category, "NETWORK")
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 6)
        # Logitech Illuminated keyboard + T430S keyboard + KVM
        self.assertEqual(self.count(devices, "KEYBOARD"), 3)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 1)
        self.assertEqual(self.count(devices, "CDROM"), 1)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 1)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "DISK"), 1)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 2)
        self.assertEqual(self.count(devices, "CAPTURE"), 2)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.verify_devices(devices, expected_devices)

    def test_PANDABOARD(self):
        devices = self.parse("PANDABOARD")
        self.assertEqual(len(devices), 13)
        # Check that the wireless product name is extracted from the platform
        # modalias
        self.assertEqual(devices[2].product, "wl12xx")
        self.assertEqual(self.count(devices, "VIDEO"), 0)
        self.assertEqual(self.count(devices, "AUDIO"), 0)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 0)
        self.assertEqual(self.count(devices, "CARDREADER"), 0)
        self.assertEqual(self.count(devices, "CDROM"), 0)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 0)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 0)
        self.assertEqual(self.count(devices, "CAPTURE"), 0)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "DISK"), 1)

    def test_SAMSUNG_N310(self):
        devices = self.parse("SAMSUNG_N310")
        self.assertEqual(len(devices), 55)
        self.assertEqual(self.count(devices, "VIDEO"), 1)
        self.assertEqual(self.count(devices, "AUDIO"), 1)
        self.assertEqual(self.count(devices, "KEYBOARD"), 1)
        self.assertEqual(self.count(devices, "TOUCHPAD"), 1)
        self.assertEqual(self.count(devices, "CARDREADER"), 0)
        self.assertEqual(self.count(devices, "CDROM"), 0)
        self.assertEqual(self.count(devices, "FIREWIRE"), 0)
        self.assertEqual(self.count(devices, "MOUSE"), 0)
        self.assertEqual(self.count(devices, "ACCELEROMETER"), 0)
        self.assertEqual(self.count(devices, "TOUCHSCREEN"), 0)
        # Check that wireless device are properly detected even if the usb
        # modalias is wrong.
        # The PCI_CLASS is 20000 for the Atheros cards in this Samsung netbook
        # but 28000 anywhere else.
        # See https://bugs.launchpad.net/checkbox/+bug/855382
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.assertEqual(self.count(devices, "DISK"), 1)
        self.assertEqual(self.count(devices, "RAID"), 0)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.assertEqual(self.count(devices, "CAPTURE"), 1)

    def test_LENOVO_T420(self):
        devices = self.parse("LENOVO_T420")
        expected_devices = {"Centrino Advanced-N 6205 [Taylor Peak]":
                            ("WIRELESS", "pci", 0x8086, 0x85),
                            "82579LM Gigabit Network Connection":
                            ("NETWORK", "pci", 0x8086, 0x1502)
                            }
        self.assertEqual(len(devices), 64)
        self.assertEqual(self.count(devices, "WIRELESS"), 1)
        self.assertEqual(self.count(devices, "BLUETOOTH"), 1)
        self.assertEqual(self.count(devices, "NETWORK"), 1)
        self.verify_devices(devices, expected_devices)

    def verify_devices(self, devices, device_dict):
        """ Verify we have exactly one of each device given in the dict,
            also that category, bus, vendor_id and product_id match.
            Contents of the dict have a key per device,
            which should be the product name, with the value
            being a tuple with categorym, bus, vendor and product.
            They look like:
            {'Device name': (category, bus, vendor_id, product_id)}
        """
        # See this bug, that prompted for closer inspection of
        # devices and IDs:
        # https://bugs.launchpad.net/checkbox/+bug/1211521
        for product, expected in device_dict.items():
            indices = [idx for idx, elem in enumerate(devices)
                       if elem.product == product]
            self.assertEqual(len(indices), 1,
                             "{} items of {} found".format(len(indices),
                                                           product))
            self.assertEqual(devices[indices[0]].category, expected[0],
                             "Bad category for {}".format(product))
            self.assertEqual(devices[indices[0]].bus, expected[1],
                             "Bad bus for {}".format(product))
            self.assertEqual(devices[indices[0]].vendor_id, expected[2],
                             "Bad vendor_id for {}".format(product))
            self.assertEqual(devices[indices[0]].product_id, expected[3],
                             "Bad product_id for {}".format(product))


class TestDecodeId(TestCase):

    def test_string(self):
        self.assertEqual("USB 2.0", decode_id("USB 2.0"))

    def test_escape(self):
        self.assertEqual("USB 2.0", decode_id("USB\\x202.0"))

    def test_strip_whitespace(self):
        self.assertEqual("USB 2.0", decode_id("  USB 2.0  "))
