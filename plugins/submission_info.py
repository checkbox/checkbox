import md5
import logging

from datetime import datetime

from hwtest.plugin import Plugin


class SubmissionInfo(Plugin):

    attributes = ["submission_id"]

    def register(self, manager):
        super(SubmissionInfo, self).register(manager)
        self._system_id = None

        for (rt, rh) in [
             ("report", self.report),
             (("report", "system_id"), self.report_system_id)]:
            self._manager.reactor.call_on(rt, rh)

    def report_system_id(self, system_id):
        self._system_id = system_id

    def report(self):
        submission_id = self.config.submission_id
        if not submission_id:
            fingerprint = md5.new()
            fingerprint.update(self._system_id)
            fingerprint.update(str(datetime.utcnow()))
            submission_id = fingerprint.hexdigest()

        message = submission_id
        logging.info("Submission ID: %s", message)
        self._manager.reactor.fire(("report", "submission_id"), message)


factory = SubmissionInfo
