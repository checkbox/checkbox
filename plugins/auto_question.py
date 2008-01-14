from hwtest.lib.environ import add_path, remove_path

from hwtest.plugin import Plugin
from hwtest.question import Question


class Auto(Question):

    required_fields = Question.required_fields + ["path"]

    def run_command(self):
        add_path(self.path)
        (stdout, stderr, wait) = super(Auto, self).run_command()
        remove_path(self.path)
        return (stdout, stderr, wait)


class AutoQuestion(Plugin):

    attributes = ["scripts_path"]

    def register(self, manager):
        super(AutoQuestion, self).register(manager)
        for (rt, rh) in [
             (("question", "auto"), self.question_auto)]:
            self._manager.reactor.call_on(rt, rh)

    def question_auto(self, question):
        kwargs = dict(question)
        kwargs["path"] = self.config.scripts_path
        question = Auto(self._manager.registry, **kwargs)
        self._manager.reactor.fire(("prompt", "auto"), question)


factory = AutoQuestion
