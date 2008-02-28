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
from gettext import gettext as _

from hwtest.plugin import Plugin
from hwtest.question import QuestionManager
from hwtest.answer import Answer


class AutoPrompt(Plugin):

    def register(self, manager):
        super(AutoPrompt, self).register(manager)
        self._question_manager = QuestionManager()
        self._done = False

        for (rt, rh) in [
             (("interface", "category"), self.interface_category),
             (("question", "auto"), self.question_auto),
             (("prompt", "auto"), self.prompt_auto)]:
            self._manager.reactor.call_on(rt, rh)

    def interface_category(self, category):
        self._question_manager.set_category(category)

    def question_auto(self, question):
        self._question_manager.add_question(question)

    def _run_auto(self):
        for question in self._question_manager.get_iterator():
            question.command()
            question.description()
            question.answer = Answer(question.command.get_status(),
                question.command.get_data())
            self._manager.reactor.fire(("report", "question"),
                question)

    def prompt_auto(self, interface):
        if self._question_manager.get_count() and not self._done:
            interface.show_wait(_("Running automatic questions..."),
                self._run_auto)
            self._done = True


factory = AutoPrompt
