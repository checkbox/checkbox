#
# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
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
import imp
import os
import unittest

imp.load_source('audio_settings', os.path.join(os.path.dirname(__file__),
                '..', '..', '..', 'scripts', 'audio_settings'))
from audio_settings import _guess_hdmi_profile
from checkbox.parsers.tests.test_pactl import PactlDataMixIn


class SetProfileTest(unittest.TestCase, PactlDataMixIn):

    def test_desktop_precise_xps1340(self):
        self.assertEqual(
            _guess_hdmi_profile(self.get_text("desktop-precise-xps1340")),
            ('0', 'output:hdmi-stereo'))

    def test_desktop_precise_radeon_not_available(self):
        self.assertEqual(
            _guess_hdmi_profile(self.get_text("desktop-precise-radeon")),
            (None, None))

    def test_desktop_precise_radeon_available(self):
        self.assertEqual(
            _guess_hdmi_profile(self.get_text(
                "desktop-precise-radeon-hdmi-available")),
            ('0', 'output:hdmi-stereo'))
