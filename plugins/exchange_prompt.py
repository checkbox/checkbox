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
import re

from gettext import gettext as _

from checkbox.plugin import Plugin
from checkbox.iterator import NEXT, PREV


class ExchangePrompt(Plugin):

    optional_attributes = ["email"]

    def register(self, manager):
        super(ExchangePrompt, self).register(manager)
        self._email_regexp = re.compile(r"^\S+@\S+.\S+$", re.I)
        self._email = None
        self._reports = []

        for (rt, rh) in [
             ("report-hal", self.report_hal),
             ("report-distribution", self.report_distribution),
             ("report-packages", self.report_packages),
             ("report-processors", self.report_processors),
             ("report-tests", self.report_tests),
             ("prompt-exchange", self.prompt_exchange)]:
            self._manager.reactor.call_on(rt, rh)

    def report_hal(self, message):
        self._reports.append("devices")

    def report_distribution(self, message):
        self._reports.append("distribution")

    def report_packages(self, message):
        self._reports.append("packages")

    def report_processors(self, message):
        self._reports.append("processors")

    def report_tests(self, message):
        self._reports.append("tests")

    def fire_exchange(self, interface):
        self._manager.reactor.fire("exchange-email", self._email)
        interface.show_wait(
            _("Exchanging information with the server..."),
            lambda: self._manager.reactor.fire("exchange"))
        return self._manager.get_error()

    def prompt_exchange(self, interface):
        error = None
        if self.config.email and interface.direction == NEXT:
            self._email = self.config.email
            error = self.fire_exchange(interface)
            if not error:
                return

        while True:
            self._email = interface.show_exchange(self._email, self._reports,
                _("""\
The following information will be sent to the Launchpad
hardware database. Please provide the e-mail address you
use to sign in to Launchpad to submit this information."""), error=error)

            if interface.direction == PREV:
                break
            elif not self._email_regexp.match(self._email):
                error = _("Email address must be in a proper format.")
            else:
                error = self.fire_exchange(interface)
                if not error:
                    break


factory = ExchangePrompt
