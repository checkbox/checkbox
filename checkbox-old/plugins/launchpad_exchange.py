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
import time
import pprint
import bz2
import logging
import posixpath

from gettext import gettext as _
from socket import gethostname
from io import BytesIO

from checkbox.lib.log import format_delta
from checkbox.lib.transport import HTTPTransport

from checkbox.properties import File, Int, Map, String
from checkbox.plugin import Plugin


FORM = Map({
    "field.private": String(),
    "field.contactable": String(),
    "field.format": String(),
    "field.actions.upload": String(),
    "field.architecture": String(),
    "field.date_created": String(),
    "field.distribution": String(),
    "field.distroseries": String(),
    "field.submission_key": String(),
    "field.system": String(),
    "field.emailaddress": String(),
    "field.live_cd": String(),
    "field.submission_data": File()})


class LaunchpadExchange(Plugin):

    # Timeout value for each submission.
    timeout = Int(default=120)

    # URL where to send submissions.
    transport_url = String(default="https://launchpad.net/+hwdb/+submit")

    def register(self, manager):
        super(LaunchpadExchange, self).register(manager)

        self._headers = {
            "Referer": self.transport_url}
        self._form = {
            "field.private": "False",
            "field.contactable": "False",
            "field.live_cd": "False",
            "field.format": "VERSION_1",
            "field.actions.upload": "Upload",
            "field.submission_data": None,
            "field.system": None}

        for (rt, rh) in [
             ("report-client", self.report_client),
             ("report-datetime", self.report_datetime),
             ("report-dpkg", self.report_dpkg),
             ("report-lsb", self.report_lsb),
             ("report-submission_id", self.report_submission_id),
             ("report-system_id", self.report_system_id),
             ("launchpad-email", self.launchpad_email),
             ("launchpad-report", self.launchpad_report),
             ("launchpad-exchange", self.launchpad_exchange)]:
            self._manager.reactor.call_on(rt, rh)

    def report_client(self, message):
        user_agent = "%s/%s" % (message["name"], message["version"])
        self._headers["User-Agent"] = user_agent

    def report_datetime(self, message):
        self._form["field.date_created"] = message

    def report_dpkg(self, resources):
        dpkg = resources[0]
        self._form["field.architecture"] = dpkg["architecture"]

    def report_lsb(self, resources):
        lsb = resources[0]
        self._form["field.distribution"] = lsb["distributor_id"]
        self._form["field.distroseries"] = lsb["release"]

    def report_submission_id(self, message):
        self._form["field.submission_key"] = message

    def report_system_id(self, message):
        self._form["field.system"] = message

    def launchpad_email(self, message):
        self._form["field.emailaddress"] = message

    def launchpad_report(self, report):
        self._launchpad_report = report

    def launchpad_exchange(self, interface):
        # Maybe on the next exchange...
        if not self._form["field.system"] \
           or self._form["field.submission_data"]:
            return

        # Compress and add payload to form
        payload = open(self._launchpad_report, "rb").read()
        compressed_payload = bz2.compress(payload)
        file = BytesIO(compressed_payload)
        file.name = "%s.xml.bz2" % gethostname()
        file.size = len(compressed_payload)
        self._form["field.submission_data"] = file

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Uncompressed payload length: %d", len(payload))

        # Encode form data
        try:
            form = FORM.coerce(self._form)
        except ValueError as e:
            self._manager.reactor.fire("exchange-error", _("""\
Failed to process form: %s""" % e))
            return

        transport = HTTPTransport(self.transport_url)
        start_time = time.time()
        try:
            response = transport.exchange(form, self._headers,
                timeout=self.timeout)
        except Exception as error:
            self._manager.reactor.fire("exchange-error", str(error))
            return
        end_time = time.time()

        if not response:
            self._manager.reactor.fire("exchange-error", _("""\
Failed to contact server. Please try
again or upload the following file name:
%s

directly to the system database:
https://launchpad.net/+hwdb/+submit""") % posixpath.abspath(self._launchpad_report))
            return
        elif response.status != 200:
            self._manager.reactor.fire("exchange-error", _("""\
Failed to upload to server,
please try again later."""))
            return

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Response headers:\n%s",
                pprint.pformat(response.getheaders()))

        header = response.getheader("x-launchpad-hwdb-submission")
        if not header:
            self._manager.reactor.fire("exchange-error",
                _("Information not posted to Launchpad."))
        elif "Error" in header:
            # HACK: this should return a useful error message
            self._manager.reactor.fire("exchange-error", header)
            logging.error(header)
        else:
            text = response.read()
            self._manager.reactor.fire("exchange-success", text)
            logging.info("Sent %d bytes and received %d bytes in %s.",
                file.size, len(text), format_delta(end_time - start_time))


factory = LaunchpadExchange
