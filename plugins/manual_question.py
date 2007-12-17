import os

from hwtest.lib.environ import add_path, remove_path, add_variable, remove_variable

from hwtest.plugin import Plugin
from hwtest.question import Question, QuestionManager


class Manual(Question):

    required_fields = Question.required_fields + ["data_path", "scripts_path"]

    def run_description(self):
        add_path(self.scripts_path)
        description = super(Manual, self).run_description()
        remove_path(self.scripts_path)
        return description

    def run_command(self):
        add_path(self.scripts_path)
        add_variable("data_path", self.data_path)
        (stdout, stderr, wait) = super(Manual, self).run_command()
        remove_variable("data_path")
        remove_path(self.scripts_path)
        return (stdout, stderr, wait)


class ManualQuestion(Plugin):

    def __init__(self, config, question_factory=None):
        super(ManualQuestion, self).__init__(config)
        self._question_factory = question_factory or Manual
        self._question_manager = QuestionManager()

    def register(self, manager):
        super(ManualQuestion, self).register(manager)

        # Manual questions should be asked first.
        for (rt, rh, rp) in [
             (("manual", "add-question"), self.add_question, -100),
             (("interface", "show-question"), self.show_question, 0)]:
            self._manager.reactor.call_on(rt, rh, rp)

    def show_question(self, interface):
        questions = self._question_manager.get_iterator()

        direction = 1
        while True:
            try:
                if direction == 1:
                    question = questions.next()
                else:
                    question = questions.prev()
            except StopIteration:
                break

            direction = interface.show_question(question, questions.has_prev())
            self._manager.reactor.fire(("report", "add-question"),
                question.properties)

    def add_question(self, question):
        kwargs = dict(question)
        kwargs["data_path"] = self.config.data_path
        kwargs["scripts_path"] = self.config.scripts_path
        question = self._question_factory(self._manager.registry, **kwargs)
        self._question_manager.add_question(question)


factory = ManualQuestion
