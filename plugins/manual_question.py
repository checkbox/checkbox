import os

from hwtest.lib.environ import add_path, remove_path, add_variable, remove_variable

from hwtest.plugin import Plugin
from hwtest.question import Question, QuestionManager


class Manual(Question):

    required_fields = Question.required_fields + ["data_path", "scripts_path"]

    def __getattr__(self, attr):
        if attr is "description":
            return self.get_description()
        else:
            return super(Manual, self).__getattr__(attr)

    def get_description(self):
        add_path(self.scripts_path)
        command = "cat <<EOF\n%s\nEOF\n" % self.properties["description"]
        description = os.popen(command).read()
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

    priority = -100

    def __init__(self, config, question_factory=None):
        super(ManualQuestion, self).__init__(config)
        self._question_factory = question_factory or Manual
        self._question_manager = QuestionManager()

    def register(self, manager):
        super(ManualQuestion, self).register(manager)
        for (rt, rh) in [(("manual", "add-question"), self.add_question),
                         (("interface", "show-question"), self.show_question)]:
            self._manager.reactor.call_on(rt, rh)

    def show_question(self, interface):
        questions = self._question_manager.get_iterator()
        question = questions.next()
        while question:
            has_prev = questions.has_prev()
            has_next = questions.has_next()
            direction = interface.show_question(question, has_prev, has_next)
            if direction is 1:
                question = has_next and questions.next() or None
            else:
                question = has_prev and questions.prev() or None

    def add_question(self, *args, **kwargs):
        kwargs["data_path"] = self.config.data_path
        kwargs["scripts_path"] = self.config.scripts_path
        question = self._question_factory(self._manager.registry,
            *args, **kwargs)
        self._question_manager.add_question(question)


factory = ManualQuestion
