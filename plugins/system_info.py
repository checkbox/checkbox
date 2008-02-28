#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
import md5
import logging

from hwtest.plugin import Plugin


class SystemInfo(Plugin):

    optional_attributes = ["system_id"]

    def register(self, manager):
        super(SystemInfo, self).register(manager)

        # System report should be generated early.
        for (rt, rh, rp) in [
             ("report", self.report, -10)]:
            self._manager.reactor.call_on(rt, rh, rp)

    def report(self):
        system_id = self.config.system_id
        if not system_id:
            system = self._manager.registry.hal.computer.system
            if not system:
                return

            # Old versions of HAL didn't have the hardware namespace
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
                    hardware.produdct]:
                fingerprint.update(str(field))

            system_id = fingerprint.hexdigest()

        message = system_id
        logging.info("System ID: %s", message)
        self._manager.reactor.fire(("report", "system_id"), message)


factory = SystemInfo
