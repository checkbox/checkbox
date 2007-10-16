from hwtest.submission import get_submission_id
from hwtest.plugin import Plugin


class SubmissionIdInfo(Plugin):

    def register(self, manager):
        super(SubmissionIdInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def gather(self):
        message = get_submission_id()
        self._manager.reactor.fire(("report", "submission_id"), message)


factory = SubmissionIdInfo
