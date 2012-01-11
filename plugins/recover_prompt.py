#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
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

from checkbox.contrib.persist import Persist, MemoryBackend

from checkbox.plugin import Plugin
from checkbox.user_interface import NEXT


class RecoverPrompt(Plugin):

    @property
    def persist(self):
        if self._persist is None:
            self._persist = Persist(backend=MemoryBackend())

        return self._persist.root_at("recover_prompt")

    def register(self, manager):
        super(RecoverPrompt, self).register(manager)

        self._persist = None

        for (rt, rh) in [
             ("begin-persist", self.begin_persist),
             ("prompt-begin", self.prompt_begin),
             ("prompt-finish", self.prompt_finish)]:
            self._manager.reactor.call_on(rt, rh)

    def begin_persist(self, persist):
        self._persist = persist

    def prompt_begin(self, interface):
        if interface.direction == NEXT \
           and self.persist.get("recover", False):
            recover = _("Recover")
            restart = _("Restart")
            response = interface.show_info(
                _("Checkbox did not finish completely.\n"
                  "Do you want to recover from the previous run?"),
                [recover, restart], recover)
            self._manager.reactor.fire("begin-recover", response == recover)

        self.persist.set("recover", True)

    def prompt_finish(self, interface):
        if interface.direction == NEXT:
            self.persist.set("recover", False)


factory = RecoverPrompt
