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
import posixpath
import re

from gettext import gettext as _

from checkbox.lib.iterator import PREV

from checkbox.properties import String
from checkbox.plugin import Plugin


class ExchangePrompt(Plugin):

    # E-mail address used to sign in to Launchpad.
    email = String(required=False)

    def register(self, manager):
        super(ExchangePrompt, self).register(manager)

        for (rt, rh) in [
             ("gather-persist", self.gather_persist),
             ("exchange-error", self.exchange_error),
             ("exchange-report", self.exchange_report),
             ("prompt-exchange", self.prompt_exchange)]:
            self._manager.reactor.call_on(rt, rh)

    def gather_persist(self, persist):
        self.persist = persist.root_at("exchange_prompt")

    def exchange_error(self, error):
        self._error = error

    def exchange_report(self, report):
        self._report = report

    def prompt_exchange(self, interface):
        email = self.persist.get("email") or self.email

        self._error = None
        while True:
            if self._error or not self.email:
                if self._error:
                    interface.show_error(_("Exchange"), self._error)

                url = "file://%s" % posixpath.abspath(self._report)

                email = interface.show_exchange(email, _("""\
The following information will be sent to the Launchpad \
hardware database.\n
[[%s|View Report]]\n
Please provide the e-mail address you use to sign in to Launchpad to \
submit this information.""" % url))


            if interface.direction == PREV:
                break
            elif not re.match(r"^\S+@\S+\.\S+$", email, re.I):
                self._error = _("Email address must be in a proper format.")
            else:
                self._error = None
                self._manager.reactor.fire("report-email", email)
                interface.show_wait(
                    _("Exchanging information with the server..."),
                    self._manager.reactor.fire, "exchange")
                if not self._error:
                    break

        self.persist.set("email", email)


factory = ExchangePrompt
