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
import logging

from datetime import datetime

from checkbox.lib.safe import safe_md5sum

from checkbox.properties import String
from checkbox.plugin import Plugin


class SubmissionInfo(Plugin):

    # Submission ID to exchange information with the server.
    submission_id = String(required=False)

    def register(self, manager):
        super(SubmissionInfo, self).register(manager)

        self._system_id = None

        for (rt, rh) in [
             ("report", self.report),
             ("report-system_id", self.report_system_id)]:
            self._manager.reactor.call_on(rt, rh)

    def report_system_id(self, system_id):
        self._system_id = system_id

    # TODO: report this upon gathering
    def report(self):
        submission_id = self.submission_id
        if not submission_id:
            if not self._system_id:
                return

            fingerprint = safe_md5sum()
            fingerprint.update(self._system_id)
            fingerprint.update(str(datetime.utcnow()))
            submission_id = fingerprint.hexdigest()

        message = submission_id
        logging.info("Submission ID: %s", message)
        self._manager.reactor.fire("report-submission_id", message)


factory = SubmissionInfo
