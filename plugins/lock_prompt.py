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
from gettext import gettext as _

from checkbox.contrib.glock import GlobalLock, LockAlreadyAcquired

from checkbox.properties import String
from checkbox.plugin import Plugin


class LockPrompt(Plugin):

    # Filename where the application lock is stored.
    filename = String(default="%(checkbox_data)s/lock")

    def register(self, manager):
        super(LockPrompt, self).register(manager)
        self._lock = None

        self._manager.reactor.call_on("prompt-begin", self.prompt_begin)

    def prompt_begin(self, interface):
        self._lock = GlobalLock(self.filename)
        try:
            self._lock.acquire()
        except LockAlreadyAcquired:
            self._manager.reactor.fire("prompt-error", interface,
                _("Another checkbox is running"),
                _("There is another checkbox running. Please close it first."))
            self._manager.reactor.stop_all()


factory = LockPrompt
