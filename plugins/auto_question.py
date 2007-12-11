from commands import getoutput

from hwtest.lib.environ import add_path, remove_path

from hwtest.plugin import Plugin
from hwtest.question import Question, QuestionManager


class Auto(Question):

    required_fields = Question.required_fields + ["path"]

    def run_command(self):
        add_path(self.path)
        output = getoutput(self.command)
        remove_path(self.path)
        return output


class AutoQuestion(Plugin):

    def __init__(self, config, question_factory=None):
        super(AutoQuestion, self).__init__(config)
        self._question_factory = question_factory or Auto
        self._question_manager = QuestionManager()

    def register(self, manager):
        super(AutoQuestion, self).register(manager)
        for (rt, rh) in [(("auto", "add-question"), self.add_question),
                         (("interface", "show-question"), self.show_question)]:
            self._manager.reactor.call_on(rt, rh)

    def show_question(self, interface):
        for question in self._question_manager.get_iterator():
            output = question.run_command()
            question.set_answer(1, output)

    def add_question(self, *args, **kwargs):
        kwargs["path"] = self.config.scripts_path
        question = self._question_factory(self._manager.registry,
            *args, **kwargs)
        self._question_manager.add_question(question)


factory = AutoQuestion
