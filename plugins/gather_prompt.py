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
from gettext import gettext as _

from hwtest.plugin import Plugin


class GatherPrompt(Plugin):

    def register(self, manager):
        super(GatherPrompt, self).register(manager)
        self._done = False

        self._manager.reactor.call_on(("prompt", "gather"), self.prompt_gather)
 
    def prompt_gather(self, interface):
        if not self._done:
            interface.show_wait(_("Gathering information from your system..."),
                lambda: self._manager.reactor.fire("gather"))
            self._done = True


factory = GatherPrompt
