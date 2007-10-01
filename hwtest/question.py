import re

from hwtest.excluder import Excluder
from hwtest.iterator import Iterator
from hwtest.repeater import PreRepeater
from hwtest.resolver import Resolver

from hwtest.answer import Answer, NO, SKIP
from hwtest.plugin import Plugin
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


class Question(Plugin):

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

    def gather(self):
        report = self._manager.report
        if not report.finalised:
            question = createElement(report, 'question', report.root)
            createElement(report, 'suite', question, 'tool')
            createElement(report, 'name', question, self.name)
            createElement(report, 'description', question, self.description)
            createElement(report, 'command', question)
            createElement(report, 'architectures', question)
            createTypedElement(report, 'categories', question, None, self.categories,
                               True, 'category')
            createElement(report, 'optional', question, self.optional)

            if self.answer:
                answer = createElement(report, 'answer', question)
                createElement(report, 'status', answer, self.answer.status)
                createElement(report, 'data', answer, self.answer.data)

    def create_answer(self, status, data='', auto=False):
        self.answer = Answer(self, status, data, auto)
        return self.answer


def parse_lines(lines):
    """Parse question lines and return the resulting list of
    dictionaries.

    Keyword arguments:
    lines -- lines containing a question
    """

    question = {}
    questions = []
    line_number = 0
    for line in lines:
        line_number += 1

        # Ignore comments
        if not line.startswith('#'):
            line = line.strip("\n")
            # Empty line is a dictionary separator
            if not line:
                if question:
                    questions.append(question)
                    question = {}
            # Starting space continues previous line
            elif line.startswith(' '):
                value = line.strip()
                if value:
                    if not question[key].endswith('\n\n'):
                        question[key] += ' '
                    question[key] += value
                else:
                    question[key] += '\n\n'
            # Otherwise, directory entry
            else:
                key, value = line.split(':', 1)
                value = value.strip()
                question[key] = value

    # Append last entry
    if question:
        questions.append(question)

    return questions

def parse_string(string):
    """Parse a question string and return the resulting list of
    dictionaries.

    Keyword arguments:
    string -- string containing a question
    """

    return parse_lines(string.split('\n'))

def parse_file(name):
    """Parse a question file and return the resulting list of
    dictionaries.

    Keyword arguments:
    name -- name of the question file
    """

    fd = file(name, 'r')
    questions = parse_lines(fd.readlines())
    fd.close()

    return questions

def parse_dir(name):
    """Parse a question directory and return the resulting list
    of dictionaries.

    Keyword arguments:
    name -- name of the question directory
    """

    # Iterate over each file in directory
    questions = []
    for root, dirnames, filenames in os.walk(name):
        for filename in filenames:
            if filename.endswith('.txt'):
                abs_filename = os.path.join(root, filename)
                questions.extend(parse_file(abs_filename))

    return questions
