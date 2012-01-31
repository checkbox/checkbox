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
from gettext import gettext as _

from checkbox.plugin import Plugin
from checkbox.properties import String
from checkbox.user_interface import PREV


class IntroPrompt(Plugin):

    welcome_text = String(default=_("""\
Welcome to System Testing!

Checkbox provides tests to confirm that your system is working \
properly. Once you are finished running the tests, you can view \
a summary report for your system.""") + _("""

Warning: Some tests could cause your system to freeze \
or become unresponsive. Please save all your work \
and close all other running applications before \
beginning the testing process."""))

    def register(self, manager):
        super(IntroPrompt, self).register(manager)

        self._recover = False

        self._manager.reactor.call_on("begin-recover", self.begin_recover)

        # Introduction should be prompted last
        self._manager.reactor.call_on("prompt-begin", self.prompt_begin, 100)

    def begin_recover(self, recover):
        self._recover = recover

    def prompt_begin(self, interface):
        if interface.direction == PREV or not self._recover:
            self._recover = False
            interface.show_text(self.welcome_text, previous="")


factory = IntroPrompt
