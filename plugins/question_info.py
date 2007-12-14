import logging

from hwtest.plugin import Plugin


class QuestionInfo(Plugin):

    def __init__(self, *args, **kwargs):
        super(QuestionInfo, self).__init__(*args, **kwargs)
        self.questions = {}

    def register(self, manager):
        super(QuestionInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)
        self._manager.reactor.call_on("report", self.report)
        self._manager.reactor.call_on(("report", "add-question"), self.add_question)

    def gather(self):
        if not self._manager.registry.questions:
            logging.info("No questions found.")
            return

        for (name, question) in self._manager.registry.questions.items():
            self._manager.reactor.fire((question.type, "add-question"), question)

    def add_question(self, question):
        self.questions[question["name"]] = question

    def report(self):
        message = self.questions.values()
        self._manager.reactor.fire(("report", "questions"), message)


factory = QuestionInfo
