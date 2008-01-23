import os
import re

from hwtest.plugin import Plugin
from hwtest.question import Question
from hwtest.template import Template


class QuestionInfo(Plugin):

    attributes = ["directories", "blacklist", "whitelist"]

    def register(self, manager):
        super(QuestionInfo, self).register(manager)
        self.questions = {}

        for (rt, rh) in [
             ("gather", self.gather),
             ("report", self.report),
             (("report", "question"), self.report_question)]:
            self._manager.reactor.call_on(rt, rh)

    def gather(self):
        def validator(template, element):
            element["suite"] = os.path.basename(template.filename)
            if [e for e in template.elements if e["name"] == element["name"]]:
                raise Exception, "Element %s already exists." % element["name"]

        directories = re.split("\s+", self.config.directories)
        blacklist = self.config.blacklist \
            and re.split("\s+", self.config.blacklist) or []
        whitelist = self.config.whitelist \
            and re.split("\s+", self.config.whitelist) or []
        template = Template(validator)
        elements = template.load_directories(directories, blacklist, whitelist)

        for element in elements:
            question = Question(self._manager.registry, **element)
            question.command.add_path(self.config.scripts_path)
            question.command.add_variable("data_path", self.config.data_path)
            self._manager.reactor.fire(("question", question.plugin), question)

    def report_question(self, question):
        self.questions[question.name] = question

    def report(self):
        message = []
        for question in self.questions.values():
            properties = question.properties
            properties["command"] = str(question.command)
            properties["description"] = str(question.description)
            properties["answer"] = question.answer.properties
            message.append(properties)
        self._manager.reactor.fire(("report", "questions"), message)


factory = QuestionInfo
