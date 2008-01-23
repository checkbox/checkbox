from hwtest.plugin import Plugin
from hwtest.question import QuestionManager


class ManualPrompt(Plugin):

    def register(self, manager):
        super(ManualPrompt, self).register(manager)
        self._question_manager = QuestionManager()

        # Manual questions should be asked first.
        for (rt, rh, rp) in [
             (("interface", "category"), self.interface_category, 0),
             (("question", "manual"), self.question_manual, 0),
             (("prompt", "questions"), self.prompt_questions, -100)]:
            self._manager.reactor.call_on(rt, rh, rp)

    def interface_category(self, category):
        self._question_manager.set_category(category)

    def question_manual(self, question):
        self._question_manager.add_question(question)

    def prompt_questions(self, interface):
        questions = self._question_manager.get_iterator(interface.direction)

        while True:
            try:
                question = questions.go(interface.direction)
            except StopIteration:
                break

            interface.do_question(question)
            self._manager.reactor.fire(("report", "question"), question)


factory = ManualPrompt
