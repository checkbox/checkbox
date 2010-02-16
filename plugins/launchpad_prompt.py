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
import re
import posixpath

from gettext import gettext as _

from checkbox.plugin import Plugin
from checkbox.properties import String
from checkbox.user_interface import PREV


class LaunchpadPrompt(Plugin):

    # E-mail address used to sign in to Launchpad.
    email = String(required=False)

    def register(self, manager):
        super(LaunchpadPrompt, self).register(manager)

        for (rt, rh) in [
             ("exchange-error", self.exchange_error),
             ("gather-persist", self.gather_persist),
             ("launchpad-report", self.launchpad_report),
             ("prompt-exchange", self.prompt_exchange)]:
            self._manager.reactor.call_on(rt, rh)

    def exchange_error(self, error):
        self._error = error

    def gather_persist(self, persist):
        self.persist = persist.root_at("launchpad_prompt")

    def launchpad_report(self, report):
        self._launchpad_report = report

    def prompt_exchange(self, interface):
        email = self.persist.get("email") or self.email

        self._error = None
        while True:
            if self._error or not self.email:
                if self._error:
                    self._manager.reactor.fire("prompt-error", interface,
                        self._error)

                url = "file://%s" % posixpath.abspath(self._launchpad_report)

                email = interface.show_entry(_("""\
The following report has been generated for submission to the Launchpad \
hardware database:

  [[%s|View Report]]

You can submit this information about your system by providing the e-mail \
address you use to sign in to Launchpad. If you do not have a Launchpad \
account, please register here:

  https://launchpad.net/+login""") % url, email)

            if interface.direction == PREV:
                break

            if not email:
                self._manager.reactor.fire("prompt-error", interface,
                    _("No e-mail address provided, not submitting to Launchpad."))
                break

            if not re.match(r"^\S+@\S+\.\S+$", email, re.I):
                self._error = _("Email address must be in a proper format.")
                continue

            self._error = None
            self._manager.reactor.fire("launchpad-email", email)
            interface.show_progress(
                _("Exchanging information with the server..."),
                self._manager.reactor.fire, "launchpad-exchange")
            if not self._error:
                break

        self.persist.set("email", email)


factory = LaunchpadPrompt
