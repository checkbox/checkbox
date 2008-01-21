from hwtest.plugin import Plugin


class ManualQuestion(Plugin):

    attributes = ["data_path", "scripts_path"]

    def register(self, manager):
        super(ManualQuestion, self).register(manager)
        for (rt, rh) in [
             (("question", "manual"), self.question_manual)]:
            self._manager.reactor.call_on(rt, rh)

    def question_manual(self, question):
        question.command.add_variable("data_path", self.config.data_path)
        question.command.add_path(self.config.scripts_path)
        self._manager.reactor.fire(("prompt", "manual"), question)


factory = ManualQuestion
