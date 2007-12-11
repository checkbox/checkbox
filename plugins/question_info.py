from hwtest.plugin import Plugin


class QuestionInfo(Plugin):

    priority = -100

    def register(self, manager):
        super(QuestionInfo, self).register(manager)
        self._manager.reactor.call_on("gather", self.gather)

    def run(self):
        for (name, question) in self._manager.registry.questions.items():
            self._manager.reactor.fire((question.type, "add-question"),
                **dict(question.items() + [('name', name)]))

    def gather(self):
        message = self._manager.registry.questions
        self._manager.reactor.fire(("report", "questions"), message)


factory = QuestionInfo
