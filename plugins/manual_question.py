import os
from commands import getoutput

from hwtest.lib.template import convert_string
from hwtest.lib.environ import add_path, remove_path

from hwtest.plugin import Plugin
from hwtest.question import Question


class Manual(Question):

    required_fields = Question.required_fields + ["path"]

    def __init__(self, config, *args, **kwargs):
        super(Manual, self).__init__(*args, **kwargs)
        self.config = config

    def __getattr__(self, attr):
        if attr is "description":
            return self.get_description()
        elif attr is "command":
            return self.get_command()
        else:
            return super(Manual, self).__getattr__(attr)

    def get_description(self):
        if self.command:
            output = self.run_command()
            description = convert_string(self.properties["description"], {'output': output})
        else:
            description = self.properties["description"]
        return description

    def get_command(self):
        command = self.properties.get("command")
        if command is not None:
            command = convert_string(command, self.config._kwargs)
        return command

    def run_command(self):
        add_path(self.path)
        output = getoutput(self.command)
        remove_path(self.path)
        return output


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
        question = self._question_factory(self.config, *args, **kwargs)
        self._manager.reactor.fire(("prompt", "add-question"), question)


factory = ManualQuestion
