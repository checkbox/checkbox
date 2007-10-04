import re

from hwtest.plugin import Plugin
from hwtest.iterator import Iterator
from hwtest.excluder import Excluder
from hwtest.question import QuestionManager, QuestionParser
from hwtest.report_helpers import createElement, createTypedElement


class QuestionPrompt(Plugin):

    run_priority = -300

    def __init__(self, config, question_manager=None):
        super(QuestionPrompt, self).__init__(config)
        self.question_manager = question_manager or QuestionManager()
        self.questions = Iterator()
        self.category = None

    def register(self, manager):
        super(QuestionPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "add-question"), self.add_question)
        self._manager.reactor.call_on(("prompt", "set-category"), self.set_category)
        self._manager.reactor.call_on(("prompt", "set-direction"), self.set_direction)

    def run(self):
        self.questions = self.get_questions()
        self.question = self.questions.next()
        while self.question:
            self._manager.reactor.fire(("interface", "show-question"),
                self.question,
                self.questions.has_prev(),
                self.questions.has_next())

    def gather(self):
        report = self._manager.report
        if not report.finalised:
            for question in iter(self.questions.iterator):
                tests = getattr(report, 'tests', None)
                if tests is None:
                    tests = createElement(report, 'tests', report.root)
                    report.tests = tests
                test = createElement(report, 'test', tests)
                createElement(report, 'suite', test, 'tool')
                createElement(report, 'name', test, question.name)
                createElement(report, 'description', test, question.description)
                createElement(report, 'command', test)
                createElement(report, 'architectures', test)
                createTypedElement(report, 'categories', test, None,
                    question.categories, True, 'category')
                createElement(report, 'optional', test, question.optional)

                if question.answer:
                    result = createElement(report, 'result', test)
                    createElement(report, 'result_status', result,
                        question.answer.status)
                    createElement(report, 'result_data', result,
                        question.answer.data)

    def add_question(self, question):
        self.question_manager.add_question(question)

    def set_category(self, category):
        self.category = category

    def set_direction(self, direction):
        questions = self.questions
        if direction is 1:
            self.question = questions.has_next() and questions.next() or None
        else:
            self.question = questions.has_prev() and questions.prev() or None

    def get_questions(self):
        parser = QuestionParser()
        for directory in re.split(r"\s*,\s*", self.config.question_dirs):
            parser.load_directory(directory)

        for question_kwargs in parser.questions:
            type = question_kwargs.pop("type")
            self._manager.reactor.fire((type, "add-question"), **question_kwargs)

        questions = self.question_manager.get_iterator()
        if self.category:
            func = lambda q, c=self.category: c not in q.categories
            questions = iter(Excluder(questions, func, func))

        return questions


factory = QuestionPrompt
