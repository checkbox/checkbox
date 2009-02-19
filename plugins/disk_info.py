#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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

from checkbox.properties import Path
from checkbox.plugin import Plugin


class DiskInfo(Plugin):

    # Filename where casper logs installation information.
    filename = Path(default="/var/log/installer/casper.log")

    def register(self, manager):
        super(DiskInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        # Try to open the disk info file logged by the installer
        try:
            file = open(self.filename)
        except IOError:
            return

        # Found label 'Ubuntu 8.04.1 _Hardy Heron_ - Release amd64 (20080702.1)'
        distributor_regex = r"(?P<distributor>[\w\-]+)"
        release_regex = r"(?P<release>[\d\.]+)"
        codename_regex = r"(?P<codename>[^_]+)"
        official_regex = r"(?P<official>[\w ]+)"
        architecture_regex = r"(?P<architecture>[\w\+]+)"
        type_regex = r"(?P<type>Binary-\d+)"
        date_regex = r"(?P<date>[^\)]+)"

        info_regex = r"%s %s _%s_ - %s %s (%s )?\(%s\)" % (distributor_regex,
            release_regex, codename_regex, official_regex, architecture_regex,
            type_regex, date_regex)
        line_regex = r"Found label '%s'" % info_regex
        line_pattern = re.compile(line_regex)

        for line in file.readlines():
            match = line_pattern.match(line)
            if match:
                keys = ["distributor", "release", "codename", "official",
                    "architecture", "date"]
                values = [match.group(k) for k in keys]
                message = dict(zip(keys, values))
                self._manager.reactor.fire("report-disk", message)
                break


factory = DiskInfo
