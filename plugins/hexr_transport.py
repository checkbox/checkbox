#
# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
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
import logging
import os
import pprint
import socket
import time
import json

from gettext import gettext as _
from http.client import HTTPException
from string import printable

from checkbox.lib.log import format_delta
from checkbox.lib.transport import HTTPTransport
from checkbox.plugin import Plugin
from checkbox.properties import Int, String


class HexrTransport(Plugin):
    """ This provides means for submitting test reports to hexr.canonical.com
        and/or certification.canonical.com
    """

    # URL where to send submissions.
    transport_url = String(default="https://hexr.canonical.com/checkbox/submit/")

    # Timeout value for each submission.
    timeout = Int(default=360)

    # Timeout value for each submission.
    max_tries = Int(default=5)

    # Header to identify the hardware ID.
    hardware_id_header = String(default="X_HARDWARE_ID")
    submit_to_hexr_header = String(default="X_SHARE_WITH_HEXR")

    def register(self, manager):
        super(HexrTransport, self).register(manager)

        self._headers = {}
        self._submission_filename = ""

        #I need to have two things in order to send the report:
        # - Filename of xml report (I get it on launchpad-report event)
        # - Hardware secure ID (I get it on report-hardware-id event)
        #
        # Fire after the report has been generated.
        self._manager.reactor.call_on("launchpad-report",
                                      self._on_get_filename)

        #This is just to get the secure_id when the report-hardware-id event
        #is fired.
        self._manager.reactor.call_on("report-hardware-id",
                                      self._on_report_hardware_id)
        self._manager.reactor.call_on("report-submit-to-hexr",
                                      self._on_report_submit_to_hexr)
        self._manager.reactor.call_on("hexr-exchange",
                                      self._on_hexr_exchange)

    def _on_report_hardware_id(self, hardware_id):
        self._headers[self.hardware_id_header] = hardware_id

    def _on_report_submit_to_hexr(self, submitToHexr):
        if submitToHexr:
            self._headers[self.submit_to_hexr_header] = 'True'
        else:
            self._headers[self.submit_to_hexr_header] = 'False'

    def _on_get_filename(self, filename):
        self._submission_filename = filename

    def _on_hexr_exchange(self, interface):
        #Ensure I have needed data!
        if not self._headers and not self._submission_filename:
            logging.debug("Not ready to submit to new cert website,"
                          "information missing")
            return

        try:
            submission_file = open(self._submission_filename, "rb")
            body = [("data", submission_file)]
        except (IOError, OSError, socket.error, HTTPException) as error:
            logging.debug(error)
            self._manager.reactor.fire("exchange-error", error)
            return

        #Pathetic attempt at slightly more robustness by retrying a few times
        #in case transmitting the submission fails due to network transient
        #glitches.

        for attempt in range(self.max_tries):
            (result, details) = self.submit_results(self.transport_url,
                                                    body,
                                                    self._headers,
                                                    self.timeout)
            if result:
                interface.show_text("Submission link: " + details)
                break
            else:
                if attempt + 1 >= self.max_tries:
                    retries_string = "I won't try again, sorry."
                else:
                    retries_string = "I will retry (try %d of %d)" % \
                                     (attempt + 1, self.max_tries)

                self._manager.reactor.fire("exchange-error",
                                           " ".join([details, retries_string]))
        #File needs to be closed :)
        submission_file.close()
        return

    def submit_results(self, transport_url, body, headers, timeout):
        transport = HTTPTransport(transport_url)
        start_time = time.time()
        submission_stat = os.fstat(body[0][1].fileno())
        submission_size = submission_stat.st_size

        try:
            response = transport.exchange(body, headers, timeout)
        except (IOError, OSError) as error:
            logging.debug(error)
            return (False, error)

        end_time = time.time()
        if not response:
            error = "Error contacting the server: %s." % transport_url
            logging.debug(error)
            return (False, error)
        elif response.status != 200:
            error = "Server returned unexpected status: %d. " % \
                    response.status
            logging.debug(error)
            return (False, error)
        else:
            #This is the only success block
            text = response.read().decode()
            status_url = json.loads(text)['url']
            if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
                logging.debug("Response headers:\n%s",
                              pprint.pformat(response.getheaders()))
                logging.debug("Response content:\n%s",
                              pprint.pformat(text))
            logging.info("Sent %d bytes and received %d bytes in %s.",
                         submission_size, len(text),
                         format_delta(end_time - start_time))
            return (True, status_url)


factory = HexrTransport
