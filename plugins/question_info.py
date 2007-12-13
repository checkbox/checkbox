from hwtest.plugin import Plugin


class QuestionInfo(Plugin):

    def register(self, manager):
        super(QuestionInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)
        self._manager.reactor.call_on("report", self.report)

    def gather(self):
        for (name, question) in self._manager.registry.questions.items():
            self._manager.reactor.fire((question.type, "add-question"),
                **dict(question.items() + [('name', name)]))

    def report(self):
        message = self._manager.registry.questions
        self._manager.reactor.fire(("report", "questions"), message)


factory = QuestionInfo
