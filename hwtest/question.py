import re
from subprocess import Popen, PIPE

from hwtest.excluder import Excluder
from hwtest.iterator import Iterator
from hwtest.repeater import PreRepeater
from hwtest.resolver import Resolver

from hwtest.answer import Answer, NO, SKIP


DESKTOP = 'desktop'
LAPTOP = 'laptop'
SERVER = 'server'
ALL_CATEGORIES = [DESKTOP, LAPTOP, SERVER]

I386 = 'i386'
AMD64 = 'amd64'
SPARC = 'sparc'
ALL_ARCHITECTURES = [I386, AMD64, SPARC]


class QuestionManager(object):

    def __init__(self):
        self._questions = []

    def add_question(self, question):
        self._questions.append(question)

    def get_iterator(self):
        def repeat_func(question, resolver):
            answer = question.answer
            if answer and (answer.status == NO or answer.status == SKIP):
                for dependent in resolver.get_dependents(question):
                    dependent.set_answer(SKIP, auto=True)

        def exclude_next_func(question):
            return question.answer != None

        def exclude_prev_func(question):
            if question.answer and question.answer.auto == True:
                question.answer = None
                return True
            else:
                return False

        resolver = Resolver()
        question_dict = dict((question.name, question) for question in self._questions)
        for question in self._questions:
            question_depends = [question_dict[d] for d in question.depends]
            resolver.add(question, *question_depends)

        questions = resolver.get_dependents()
        questions_iter = Iterator(questions)
        repeater_iter = PreRepeater(questions_iter,
            lambda question, resolver=resolver: repeat_func(question, resolver))
        excluder_iter = Excluder(repeater_iter,
            exclude_next_func, exclude_prev_func)

        return excluder_iter


class Question(object):

    required_fields = ["name", "type", "description", "suite"]
    optional_fields = {
        "architectures": ALL_ARCHITECTURES,
        "categories": ALL_CATEGORIES,
        "depends": [],
        "relations": None,
        "command": None,
        "optional": False}

    def __init__(self, registry, **kwargs):
        self.registry = registry
        self.properties = kwargs
        self.answer = None
        self._validate()

    def get_properties(self):
        properties = {}
        for f in Question.required_fields + Question.optional_fields.keys():
            properties[f] = self.properties[f]
        if self.answer:
            properties['answer'] = self.answer.get_properties()
        return properties

    def _validate(self):
        # Unknown fields
        for field in self.properties.keys():
            if field not in self.required_fields + self.optional_fields.keys():
                raise Exception, \
                    "Question properties contains unknown field: %s" \
                    % field

        # Required fields
        for field in self.required_fields:
            if not self.properties.has_key(field):
                raise Exception, \
                    "Question properties does not contain a '%s': %s" \
                    % (field, properties)

        # Typed fields
        for field in ["architectures", "categories", "depends"]:
            if self.properties.has_key(field):
                self.properties[field] = re.split(r"\s*,\s*", self.properties[field])

        # Optional fields
        for field in self.optional_fields.keys():
            if not self.properties.has_key(field):
                self.properties[field] = self.optional_fields[field]

        if self.properties.has_key("relations"):
            self.properties["relations"] = self.registry.eval_recursive(self.properties["relations"])

    def __str__(self):
        return self.name

    def __getattr__(self, attr):
        if attr in self.properties:
            return self.properties[attr]

        raise AttributeError, attr

    def run_command(self):
        process = Popen([self.command], shell=True,
            stdin=None, stdout=PIPE, stderr=PIPE,
            close_fds=True)
        (stdout, stderr) = process.communicate()
        return (stdout, stderr, process.wait())

    def set_answer(self, status, data='', auto=False):
        self.answer = Answer(self, status, data, auto)
