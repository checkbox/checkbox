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
from hwtest.plugin import Plugin
from hwtest.question import QuestionManager


class ManualPrompt(Plugin):

    def register(self, manager):
        super(ManualPrompt, self).register(manager)
        self._question_manager = QuestionManager()

        # Manual questions should be asked first.
        for (rt, rh) in [
             (("interface", "category"), self.interface_category),
             (("question", "manual"), self.question_manual),
             (("question", "interactive"), self.question_manual),
             (("prompt", "manual"), self.prompt_manual)]:
            self._manager.reactor.call_on(rt, rh)

    def interface_category(self, category):
        self._question_manager.set_category(category)

    def question_manual(self, question):
        self._question_manager.add_question(question)

    def prompt_manual(self, interface):
        questions = self._question_manager.get_iterator(interface.direction)

        while True:
            try:
                question = questions.go(interface.direction)
            except StopIteration:
                break

            interface.show_question(question, question.plugin == "manual")
            self._manager.reactor.fire(("report", "question"), question)


factory = ManualPrompt
