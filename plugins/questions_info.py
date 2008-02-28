#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
import re

from hwtest.plugin import Plugin
from hwtest.question import Question
from hwtest.template import Template


class QuestionsInfo(Plugin):

    required_attributes = ["directories", "scripts_path", "data_path"]
    optional_attributes = ["blacklist", "whitelist"]

    def register(self, manager):
        super(QuestionsInfo, self).register(manager)
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
            for command in question.command, question.description:
                command.add_path(self.config.scripts_path)
                command.add_variable("data_path", self.config.data_path)

            self._manager.reactor.fire(("question", question.plugin), question)

    def report_question(self, question):
        self.questions[question.name] = question

    def report(self):
        message = []
        for question in self.questions.values():
            attributes = dict(question.attributes)
            attributes["command"] = str(question.command)
            attributes["description"] = str(question.description)
            attributes["answer"] = question.answer.attributes
            message.append(attributes)
        self._manager.reactor.fire(("report", "questions"), message)


factory = QuestionsInfo
