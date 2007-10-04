import os
from commands import getoutput

from hwtest.lib.template import convert_string
from hwtest.lib.environ import add_path, remove_path

from hwtest.plugin import Plugin
from hwtest.question import Question


class Manual(Question):

    required_fields = Question.required_fields + ["path"]

    def __getattr__(self, attr):
        if attr is "description":
            return self.get_description()
        else:
            return super(Manual, self).__getattr__(attr)

    def run_command(self):
        add_path(self.path)
        output = getoutput(self.command)
        remove_path(self.path)
        return output

    def get_description(self):
        if self.command:
            output = self.run_command()
            description = convert_string(self.data["description"], {'output': output})
        else:
            description = self.data["description"]
        return description


class ManualQuestion(Plugin):

    def __init__(self, config, question_factory=None):
        super(ManualQuestion, self).__init__(config)
        self._question_factory = question_factory or Manual

    def register(self, manager):
        super(ManualQuestion, self).register(manager)
        self._manager.reactor.call_on(("manual", "add-question"),
            self.add_question)

    def add_question(self, *args, **kwargs):
        kwargs["path"] = self.config.scripts_path
        question = self._question_factory(*args, **kwargs)
        self._manager.reactor.fire(("prompt", "add-question"), question)


factory = ManualQuestion
