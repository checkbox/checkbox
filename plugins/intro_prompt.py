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


class IntroPrompt(Plugin):

    def register(self, manager):
        super(IntroPrompt, self).register(manager)
        # Introduction should be prompted last
        self._manager.reactor.call_on("prompt-begin", self.prompt_begin, 100)

    def prompt_begin(self, interface):
        interface.show_intro(_("Welcome to System Testing!"),
            _("""\
This application will gather information from your system. Then, \
you will be asked manual tests to confirm that the system is working \
properly. Finally, you will be asked for the e-mail address you use \
to sign in to Launchpad in order to submit the information and your \
results.

If you do not have a Launchpad account, please register here:

  https://launchpad.net/+login

Thank you for taking the time to test your system."""))


factory = IntroPrompt
