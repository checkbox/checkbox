#
# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
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

from unittest import TestCase

from checkbox.parsers.udevadm import UdevadmParser, decode_id


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


class TestUdevadmParser(TestCase):

    def getParser(self, string):
        stream = StringIO(string)
        return UdevadmParser(stream)

    def getResult(self, string):
        parser = self.getParser(string)
        result = DeviceResult()
        parser.run(result)
        return result

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


class TestDecodeId(TestCase):

    def test_string(self):
        self.assertEqual("USB 2.0", decode_id("USB 2.0"))

    def test_escape(self):
        self.assertEqual("USB 2.0", decode_id("USB\\x202.0"))

    def test_strip_whitespace(self):
        self.assertEqual("USB 2.0", decode_id("  USB 2.0  "))
