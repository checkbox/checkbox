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
import logging

from checkbox.lib.dmi import Dmi
from checkbox.lib.file import write
from checkbox.lib.safe import safe_md5sum

from checkbox.properties import Path, String
from checkbox.plugin import Plugin


class SystemInfo(Plugin):

    # System ID to exchange information with the server.
    system_id = String(required=False)

    # Filename where System ID is cached
    filename = Path(default="%(checkbox_data)s/system")

    def register(self, manager):
        super(SystemInfo, self).register(manager)

        self.resource = None

        for (rt, rh) in [
             ("begin-persist", self.begin_persist),
             ("report-device", self.report_device)]:
            self._manager.reactor.call_on(rt, rh)

        # System report should be generated early.
        self._manager.reactor.call_on("report", self.report, -10)

    def begin_persist(self, persist):
        self.persist = persist.root_at("system_info")

    def report_device(self, resources):
        for resource in resources:
           if resource.get("category") == "CHASSIS":
               self.resource = resource

    # TODO: report this upon gathering
    def report(self):
        system_id = self.system_id or self.persist.get("system_id")
        if not system_id:
            resource = self.resource
            if resource is None or "product" not in resource:
                return

            chassis_type = Dmi.chassis_name_to_type[resource["product"]]

            fingerprint = safe_md5sum()
            for field in [
                    "Computer",
                    "unknown",
                    chassis_type,
                    resource.get("vendor", ""),
                    resource.get("model", "")]:
                fingerprint.update(str(field))

            system_id = fingerprint.hexdigest()
            self.persist.set("system_id", system_id)

        message = system_id
        logging.info("System ID: %s", message)
        write(self.filename, message)
        self._manager.reactor.fire("report-system_id", message)


factory = SystemInfo
