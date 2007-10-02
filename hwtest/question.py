import re

from hwtest.excluder import Excluder
from hwtest.iterator import Iterator
from hwtest.repeater import PreRepeater
from hwtest.resolver import Resolver
from hwtest.plugin import Plugin

from hwtest.answer import Answer, NO, SKIP
from hwtest.template import convert_string

from hwtest.report_helpers import createElement, createTypedElement

DESKTOP = 'desktop'
LAPTOP = 'laptop'
SERVER = 'server'
ALL_CATEGORIES = [DESKTOP, LAPTOP, SERVER]


class QuestionManager(object):
    def __init__(self):
        self.questions = []

    def add(self, question):
        self.questions.append(question)

    def get_iterator(self):
        def repeat_func(question, resolver):
            answer = question.answer
            if answer and (answer.status == NO or answer.status == SKIP):
                for dependent in resolver.get_dependents(question):
                    dependent.create_answer(SKIP, auto=True)

        def exclude_next_func(question):
            return question.answer != None

        def exclude_prev_func(question):
            if question.answer and question.answer.auto == True:
                question.answer = None
                return True
            else:
                return False

        resolver = Resolver()
        question_dict = dict((question.name, question) for question in self.questions)
        for question in self.questions:
            question_deps = [question_dict[dep] for dep in question.deps]
            resolver.add(question, *question_deps)

        questions = resolver.get_dependents()
        questions_iter = Iterator(questions)
        repeater_iter = PreRepeater(questions_iter,
            lambda question, resolver=resolver: repeat_func(question, resolver))
        excluder_iter = Excluder(repeater_iter,
            exclude_next_func, exclude_prev_func)

        return excluder_iter


class Question(object):

    def __init__(self, name, desc, deps=[], cats=ALL_CATEGORIES, optional=False, command=None):
        self.name = self.persist_name = name
        self.desc = desc
        self.deps = deps
        self.cats = cats
        self.optional = optional
        self.command = command
        self.answer = None

    def __str__(self):
        return self.name
    
    @property
    def description(self):
        description = self.desc
        if self.command:
            result = self.command()
            description = convert_string(self.desc, {'result': result})

        return description

    @property
    def categories(self):
        return self.cats

    def create_answer(self, status, data='', auto=False):
        self.answer = Answer(self, status, data, auto)
        return self.answer


class QuestionPlugin(Plugin):

    run_priority = -500

    questions = []

    def gather(self):
        report = self._manager.report
        if not report.finalised:
            for q in self.questions:
                question = createElement(report, 'question', report.root)
                createElement(report, 'suite', question, 'tool')
                createElement(report, 'name', question, q.name)
                createElement(report, 'description', question, q.description)
                createElement(report, 'command', question)
                createElement(report, 'architectures', question)
                createTypedElement(report, 'categories', question, None, q.categories,
                                   True, 'category')
                createElement(report, 'optional', question, q.optional)

                if q.answer:
                    answer = createElement(report, 'answer', question)
                    createElement(report, 'status', answer, q.answer.status)
                    createElement(report, 'data', answer, q.answer.data)

    def run(self):
        for question in self.questions:
            self._manager.reactor.fire(("prompt", "add-question"), question)
