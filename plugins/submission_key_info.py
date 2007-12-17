import logging

from hwtest.submission import get_submission_key
from hwtest.plugin import Plugin


class SubmissionKeyInfo(Plugin):

    def register(self, manager):
        super(SubmissionKeyInfo, self).register(manager)
        self._manager.reactor.call_on("report", self.report)

    def report(self):
        message = get_submission_key(self._manager.registry)
        logging.info("Submission key: %s", message)
        self._manager.reactor.fire(("report", "submission_key"), message)


factory = SubmissionKeyInfo
