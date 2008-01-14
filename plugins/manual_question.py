from hwtest.lib.environ import (add_path, remove_path, add_variable,
    remove_variable)

from hwtest.plugin import Plugin
from hwtest.question import Question


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

    attributes = ["data_path", "scripts_path"]

    def register(self, manager):
        super(ManualQuestion, self).register(manager)
        for (rt, rh) in [
             (("question", "manual"), self.question_manual)]:
            self._manager.reactor.call_on(rt, rh)

    def question_manual(self, question):
        kwargs = dict(question)
        kwargs["data_path"] = self.config.data_path
        kwargs["scripts_path"] = self.config.scripts_path
        question = Manual(self._manager.registry, **kwargs)
        self._manager.reactor.fire(("prompt", "manual"), question)


factory = ManualQuestion
