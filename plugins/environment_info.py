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

from checkbox.plugin import Plugin
from checkbox.properties import String

class EnvironmentInfo(Plugin):

    routers = String(default="single")
    router_ssid = String(default="")
    router_psk = String(default="")

    wpa_bg_ssid = String(default="")
    wpa_bg_psk = String(default="")
    open_bg_ssid = String(default="")
    wpa_n_ssid = String(default="")
    wpa_n_psk = String(default="")
    open_n_ssid = String(default="")

    def register(self, manager):
        super(EnvironmentInfo, self).register(manager)

        self._manager.reactor.call_on("prompt-begin", self.prompt_begin, 100)

    def prompt_begin(self, interface):
        os.environ['ROUTERS'] = self.routers

        os.environ['ROUTER_SSID'] = self.router_ssid
        os.environ['ROUTER_PSK'] = self.router_psk

        os.environ['WPA_BG_SSID'] = self.wpa_bg_ssid
        os.environ['WPA_BG_PSK'] = self.wpa_bg_psk
        os.environ['OPEN_BG_SSID'] = self.open_bg_ssid
        os.environ['WPA_N_SSID'] = self.wpa_bg_ssid
        os.environ['WPA_N_PSK'] = self.wpa_bg_psk
        os.environ['OPEN_N_SSID'] = self.open_n_ssid

factory = EnvironmentInfo
