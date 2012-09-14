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
import os

from unittest import TestCase

from checkbox.parsers.xinput import XinputParser


class XinputResult:

    def __init__(self):
        self.devices = {}

    def addXinputDevice(self, device):
        self.devices[device["id"]] = device

    def addXinputDeviceClass(self, device, device_class):
        self.devices[device["id"]].setdefault("classes", [])
        self.devices[device["id"]]["classes"].append(device_class)


class TestXinputParser(TestCase):

    def getFixture(self, name):
        return os.path.join(os.path.dirname(__file__), "fixtures", name)

    def getParser(self, name):
        fixture = self.getFixture(name)
        stream = open(fixture)
        return XinputParser(stream)

    def getResult(self, name):
        parser = self.getParser(name)
        result = XinputResult()
        parser.run(result)
        return result

    def test_number_of_devices_with_spaces(self):
        """The toshiba xinput with spaces contains 12 devices."""
        result = self.getResult("xinput_toshiba.txt")
        self.assertEquals(len(result.devices), 12)

    def test_number_of_devices_without_spaces(self):
        """The quantal xinput without spaces contains 14 devices."""
        result = self.getResult("xinput_quantal.txt")
        self.assertEquals(len(result.devices), 14)

    def test_multitouch_touchpad_device(self):
        """The toshiba xinput contains a multitouch touchpad device."""
        result = self.getResult("xinput_toshiba.txt")
        devices = [device for device in result.devices.values()
            if device["name"] == "AlpsPS/2 ALPS DualPoint TouchPad"]
        self.assertEquals(len(devices), 1)

        classes = [cls for cls in devices[0]["classes"]
            if cls["class"] == "XITouchClass"]
        self.assertEquals(len(classes), 1)
        self.assertEquals(classes[0]["touch_mode"], "dependent")

    def test_multitouch_touchscreen_device(self):
        """The quantal xinput contains a multitouch touchscreen device."""
        result = self.getResult("xinput_quantal.txt")
        devices = [device for device in result.devices.values()
            if device["name"] == "Quanta OpticalTouchScreen"]
        self.assertEquals(len(devices), 1)

        classes = [cls for cls in devices[0]["classes"]
            if cls["class"] == "XITouchClass"]
        self.assertEquals(len(classes), 1)
        self.assertEquals(classes[0]["touch_mode"], "direct")
