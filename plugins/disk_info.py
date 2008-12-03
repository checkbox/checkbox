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
import re
import posixpath

from checkbox.plugin import Plugin


class DiskInfo(Plugin):

    required_attributes = ["filename"]

    def register(self, manager):
        super(DiskInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        # Found label 'Ubuntu 8.04.1 _Hardy Heron_ - Release amd64 (20080702.1)'
        filename = self._config.filename
        if posixpath.exists(filename):
            file = open(filename)
            regex = re.compile(r"Found label '([\w\-]+) ([\d\.]+) _([^_]+)_ "
                "- ([\w ]+) (i386|amd64|powerpc|sparc) "
                "(Binary-\d+ )?\(([^\)]+)\)'")
            for line in file.readlines():
                match = regex.match(line)
                if match:
                    message = {
                        "distributor": match.group(1),
                        "release": match.group(2),
                        "codename": match.group(3),
                        "official": match.group(4),
                        "architecture": match.group(5),
                        "date": match.group(7)}
                    self._manager.reactor.fire("report-disk", message)
                    break


factory = DiskInfo
