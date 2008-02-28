from gettext import gettext as _

from hwtest.plugin import Plugin
from hwtest.question import QuestionManager
from hwtest.answer import Answer


class AutoPrompt(Plugin):

    def register(self, manager):
        super(AutoPrompt, self).register(manager)
        self._question_manager = QuestionManager()
        self._done = False

        for (rt, rh) in [
             (("interface", "category"), self.interface_category),
             (("question", "auto"), self.question_auto),
             (("prompt", "auto"), self.prompt_auto)]:
            self._manager.reactor.call_on(rt, rh)

    def interface_category(self, category):
        self._question_manager.set_category(category)

    def question_auto(self, question):
        self._question_manager.add_question(question)

    def _run_auto(self):
        for question in self._question_manager.get_iterator():
            question.command()
            question.description()
            question.answer = Answer(question.command.get_status(),
                question.command.get_data())
            self._manager.reactor.fire(("report", "question"),
                question)

    def prompt_auto(self, interface):
        if self._question_manager.get_count() or not self._done:
            interface.show_wait(_("Running automatic questions..."),
                self._run_auto)
            self._done = True


factory = AutoPrompt
