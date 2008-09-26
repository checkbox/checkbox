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
import md5
import logging

from checkbox.plugin import Plugin


class SystemInfo(Plugin):

    optional_attributes = ["system_id"]

    def register(self, manager):
        super(SystemInfo, self).register(manager)

        # System report should be generated early.
        self._manager.reactor.call_on("report", self.report, -10)

    def report(self):
        system_id = self._config.system_id or self._persist.get("system_id")
        if not system_id:
            system = self._manager.registry.hal.computer.system
            if not system:
                return

            # Old versions of HAL didn't have the system namespace
            if "hardware" in system:
                hardware = system.hardware
            else:
                hardware = system

            fingerprint = md5.new()
            for field in [
                    system.info.product,
                    system.info.subsystem,
                    system.product,
                    system.vendor,
                    system.formfactor,
                    hardware.vendor,
                    hardware.product]:
                fingerprint.update(str(field))

            system_id = fingerprint.hexdigest()
            self._persist.set("system_id", system_id)

        message = system_id
        logging.info("System ID: %s", message)
        self._manager.reactor.fire("report-system_id", message)


factory = SystemInfo
