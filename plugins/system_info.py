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

from checkbox.lib.safe import safe_md5sum

from checkbox.properties import String
from checkbox.plugin import Plugin


class SystemInfo(Plugin):

    # System ID to exchange information with the server.
    system_id = String(required=False)

    def register(self, manager):
        super(SystemInfo, self).register(manager)

        # System report should be generated early.
        self._manager.reactor.call_on("report", self.report, -10)

        self._manager.reactor.call_on("gather-persist", self.gather_persist)

    def gather_persist(self, persist):
        self.persist = persist.root_at("system_info")

    def report(self):
        system_id = self.system_id or self.persist.get("system_id")
        if not system_id:
            computer = self._manager.registry.hal.computer
            if not computer:
                return

            system = computer.system
            if not system:
                return

            # Old versions of HAL didn't have the system namespace
            if "hardware" in system:
                hardware = system.hardware
            else:
                hardware = system

            fingerprint = safe_md5sum()
            for field in [
                    computer.info.product,
                    computer.info.subsystem,
                    system.product,
                    system.vendor,
                    system.formfactor,
                    hardware.vendor,
                    hardware.product]:
                fingerprint.update(str(field))

            system_id = fingerprint.hexdigest()
            self.persist.set("system_id", system_id)

        message = system_id
        logging.info("System ID: %s", message)
        self._manager.reactor.fire("report-system_id", message)


factory = SystemInfo
