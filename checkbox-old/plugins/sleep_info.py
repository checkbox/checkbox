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
import logging

from time import sleep

from checkbox.plugin import Plugin


class SleepInfo(Plugin):

    def register(self, manager):
        super(SleepInfo, self).register(manager)

        # Sleep exchange should be called first
        for (rt, rh) in [
             ("sleep", self.sleep)]:
            self._manager.reactor.call_on(rt, rh)

    def sleep(self, message):
        timeout = float(message["timeout"])
        logging.debug("Server requested sleeping for: %s", timeout)
        sleep(timeout)


factory = SleepInfo
