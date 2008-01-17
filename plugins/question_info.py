import logging

from hwtest.plugin import Plugin


class QuestionInfo(Plugin):

    def register(self, manager):
        super(QuestionInfo, self).register(manager)
        self.questions = {}

        for (rt, rh) in [
             ("gather", self.gather),
             ("report", self.report),
             (("report", "question"), self.report_question)]:
            self._manager.reactor.call_on(rt, rh)

    def gather(self):
        if not self._manager.registry.questions:
            logging.info("No questions found.")
            return

        for (name, question) in self._manager.registry.questions.items():
            if not question.plugin:
                raise Exception, \
                    "Question does not contain 'plugin' attribute: %s" % name
            self._manager.reactor.fire(("question", question.plugin), question)

    def report_question(self, question):
        self.questions[question.name] = question

    def report(self):
        message = []
        for question in self.questions.values():
            message.append(question.get_properties())
        self._manager.reactor.fire(("report", "questions"), message)


factory = QuestionInfo
