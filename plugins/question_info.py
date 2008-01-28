import os
import re

from hwtest.plugin import Plugin
from hwtest.question import Question
from hwtest.template import Template


class QuestionInfo(Plugin):

    required_attributes = ["directories", "scripts_path", "data_path"]
    optional_attributes = ["blacklist", "whitelist"]

    def register(self, manager):
        super(QuestionInfo, self).register(manager)
        self.questions = {}

        for (rt, rh) in [
             ("gather", self.gather),
             ("report", self.report),
             (("report", "question"), self.report_question)]:
            self._manager.reactor.call_on(rt, rh)

    def gather(self):
        directories = re.split("\s+", self.config.directories)
        blacklist = self.config.blacklist \
            and re.split("\s+", self.config.blacklist) or []
        whitelist = self.config.whitelist \
            and re.split("\s+", self.config.whitelist) or []
        template = Template("suite", ["name"])
        elements = template.load_directories(directories, blacklist, whitelist)

        for element in elements:
            question = Question(self._manager.registry, element)
            question.command.add_path(self.config.scripts_path)
            question.command.add_variable("data_path", self.config.data_path)
            self._manager.reactor.fire(("question", question.plugin), question)

    def report_question(self, question):
        self.questions[question.name] = question

    def report(self):
        message = []
        for question in self.questions.values():
            attributes = question.attributes
            attributes["command"] = str(question.command)
            attributes["description"] = str(question.description)
            attributes["answer"] = question.answer.attributes
            message.append(attributes)
        self._manager.reactor.fire(("report", "questions"), message)


factory = QuestionInfo
