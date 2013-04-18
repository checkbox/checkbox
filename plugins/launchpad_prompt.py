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

    # Email address used to sign in to Launchpad.
    email = String(required=False)

    # Default email address used for anonymous submissions.
    default_email = String(default="ubuntu-friendly-squad@lists.launchpad.net")

    def register(self, manager):
        super(LaunchpadPrompt, self).register(manager)

        self.persist = None

        for (rt, rh) in [
             ("begin-persist", self.begin_persist),
             ("launchpad-report", self.launchpad_report),
             ("prompt-exchange", self.prompt_exchange)]:
            self._manager.reactor.call_on(rt, rh)

    def begin_persist(self, persist):
        self.persist = persist.root_at("launchpad_prompt")

    def launchpad_report(self, report):
        self.report = report

    def prompt_exchange(self, interface):
        if self.persist and self.persist.has("email"):
            email = self.persist.get("email")
        else:
            email = self.email

        # Register temporary handler for exchange-error events
        errors = []

        def exchange_error(e):
            errors.append(e)

        event_id = self._manager.reactor.call_on("exchange-error",
                                                 exchange_error)

        while True:
            if errors or not self.email:
                for error in errors:
                    self._manager.reactor.fire("prompt-error",
                                               interface, error)

                url = "file://%s" % posixpath.abspath(self.report)

                email = interface.show_entry(_("""\
The following report has been generated for submission to the Launchpad \
hardware database:

  [[%s|View Report]]

You can submit this information about your system by providing the email \
address you use to sign in to Launchpad. If you do not have a Launchpad \
account, please register here:

  https://launchpad.net/+login""") % url, email, label=_("Email") + ":")

            if interface.direction == PREV:
                break

            if not email:
                email = self.default_email

            if not re.match(r"^\S+@\S+\.\S+$", email, re.I):
                errors.append(_("Email address must be in a proper format."))
                continue

            errors = []
            self._manager.reactor.fire("launchpad-email", email)
            interface.show_progress(
                _("Exchanging information with the server..."),
                self._manager.reactor.fire, "launchpad-exchange", interface)
            if not errors:
                break

        self._manager.reactor.cancel_call(event_id)
        if self.persist:
            self.persist.set("email", email)


factory = LaunchpadPrompt
