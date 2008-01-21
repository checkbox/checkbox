from hwtest.plugin import Plugin


class AutoQuestion(Plugin):

    attributes = ["scripts_path"]

    def register(self, manager):
        super(AutoQuestion, self).register(manager)
        for (rt, rh) in [
             (("question", "auto"), self.question_auto)]:
            self._manager.reactor.call_on(rt, rh)

    def question_auto(self, question):
        question.command.add_path(self.config.scripts_path)
        self._manager.reactor.fire(("prompt", "auto"), question)


factory = AutoQuestion
