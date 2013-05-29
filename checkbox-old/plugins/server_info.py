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
from checkbox.lib.environ import add_variable

from checkbox.plugin import Plugin
from checkbox.properties import String


class ServerInfo(Plugin):

    transfer_server = String(default="cdimage.ubuntu.com")
    ntp_server = String(default="ntp.ubuntu.com")
    other_server = String(default="127.0.0.1")

    def register(self, manager):
        super(ServerInfo, self).register(manager)

        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        add_variable("TRANSFER_SERVER", self.transfer_server)
        add_variable("NTP_SERVER", self.ntp_server)
        add_variable("OTHER_SERVER", self.ntp_server)


factory = ServerInfo
