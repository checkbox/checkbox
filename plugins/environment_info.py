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
from checkbox.variables import get_variables


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
    btdevaddr = String(default="")
    apn = String(default="")
    conn_name = String(default="")
    username = String(default="")
    password = String(default="")
    sources_list = String(default="/etc/apt/sources.list")
    repositories = String(default="")

    def register(self, manager):
        super(EnvironmentInfo, self).register(manager)

        self._manager.reactor.call_on("prompt-begin", self.prompt_begin, 100)

    def prompt_begin(self, interface):
        for key, value in get_variables(self).items():
            name = key.name.upper()
            if name not in os.environ:
                os.environ[name] = value.get()


factory = EnvironmentInfo
