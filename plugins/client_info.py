#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
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
import posixpath

from checkbox.plugin import Plugin


class ClientInfo(Plugin):

    def register(self, manager):
        super(ClientInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = {}
        message["name"] = posixpath.basename(self._config.parent.path) \
            .replace(".ini", "")
        message["version"] = self._config.parent.get_defaults().version
        self._manager.reactor.fire("report-client", message)


factory = ClientInfo
