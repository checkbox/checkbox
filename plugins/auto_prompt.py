from hwtest.plugin import Plugin
from hwtest.question import QuestionManager
from hwtest.answer import Answer, YES, NO


class AutoPrompt(Plugin):

    def register(self, manager):
        super(AutoPrompt, self).register(manager)
        self._question_manager = QuestionManager()
        self._done = False

        for (rt, rh) in [
             (("interface", "category"), self.interface_category),
             (("question", "auto"), self.question_auto),
             (("prompt", "questions"), self.prompt_questions)]:
            self._manager.reactor.call_on(rt, rh)

    def interface_category(self, category):
        self._question_manager.set_category(category)

    def question_auto(self, question):
        self._question_manager.add_question(question)

    def prompt_questions(self, interface):
        if not self._done:
            def run_questions(self):
                for question in self._question_manager.get_iterator():
                    question.command()
                    question.description()
                    question.answer = Answer(question.command.get_status(),
                        question.command.get_data())
                    self._manager.reactor.fire(("report", "question"),
                        question)

            interface.do_wait(lambda self=self: run_questions(self),
                "Running automatic questions...")
            self._done = True


factory = AutoPrompt
