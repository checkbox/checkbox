import md5
import logging

from datetime import datetime

from hwtest.plugin import Plugin


class SubmissionKeyInfo(Plugin):

    attributes = ["submission_key"]

    def register(self, manager):
        super(SubmissionKeyInfo, self).register(manager)
        self._system_key = None

        for (rt, rh) in [
             ("report", self.report),
             (("report", "system_key"), self.report_system_key)]:
            self._manager.reactor.call_on(rt, rh)

    def report_system_key(self, system_key):
        self._system_key = system_key

    def report(self):
        submission_key = self.config.submission_key
        if not submission_key:
            fingerprint = md5.new()
            fingerprint.update(self._system_key)
            fingerprint.update(str(datetime.utcnow()))
            submission_key = fingerprint.hexdigest()

        message = submission_key
        logging.info("Submission key: %s", message)
        self._manager.reactor.fire(("report", "submission_key"), message)


factory = SubmissionKeyInfo
