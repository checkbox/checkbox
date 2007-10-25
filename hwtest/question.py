import os
import re
import types
import logging

from StringIO import StringIO

from hwtest.excluder import Excluder
from hwtest.iterator import Iterator
from hwtest.repeater import PreRepeater
from hwtest.resolver import Resolver

from hwtest.answer import Answer, NO, SKIP
from hwtest.lib.file import reader


DESKTOP = 'desktop'
LAPTOP = 'laptop'
SERVER = 'server'
ALL_CATEGORIES = [DESKTOP, LAPTOP, SERVER]

I386 = 'i386'
AMD64 = 'amd64'
SPARC = 'sparc'
ALL_ARCHITECTURES = [I386, AMD64, SPARC]


class QuestionParser(object):

    def __init__(self):
        self.questions = []

    def _load_properties(self, **properties):
        if "name" not in properties:
            raise Exception, \
                "Question properties does not contain a 'name': %s" % properties

        logging.info("Loading question properties for: %s", properties["name"])

        if filter(lambda q: q["name"] == properties["name"], self.questions):
            raise Exception, \
                "Question %s already has a question of the same name." \
                % properties["name"]

        self.questions.append(properties)

    def _load_descriptor(self, fd, name):
        for string in reader(fd):
            if not string:
                break

            properties = {}

            def _save(field, value, extended, name):
                if value and extended:
                    raise Exception, \
                        "Path %s has both a value and an extended value." % name
                extended = extended.rstrip("\n")
                if field:
                    if properties.has_key(field):
                        raise Exception, \
                            "Path %s has a duplicate field '%s' with a new value '%s'." \
                            % (name, field, value)
                    properties[field] = value or extended

            string = string.strip("\n")
            field = value = extended = ''
            for line in string.split("\n"):
                line.strip()
                match = re.search(r"^([-_.A-Za-z0-9]*):\s?(.*)", line)
                if match:
                    _save(field, value, extended, name)
                    field = match.groups()[0].lower()
                    value = match.groups()[1].rstrip()
                    extended = ''
                    basefield = re.sub(r"-.+$", "", field)
                    continue

                if re.search(r"^\s\.$", line):
                    extended += "\n\n"
                    continue

                match = re.search(r"^\s(\s+.*)", line)
                if match:
                    bit = match.groups()[0].rstrip()
                    if len(extended) and not re.search(r"[\n ]$", extended):
                        extended += "\n"

                    extended += bit + "\n"
                    continue

                match = re.search(r"^\s(.*)", line)
                if match:
                    bit = match.groups()[0].rstrip()
                    if len(extended) and not re.search(r"[\n ]$", extended):
                        extended += " "

                    extended += bit
                    continue

                raise Exception, "Path %s parse error at: %s" \
                    % (name, line)

            _save(field, value, extended, name)
            self._load_properties(**properties)

    def load_string(self, str):
        logging.info("Loading question from string")
        fd = StringIO(str)
        self._load_descriptor(fd, "string")

    def load_path(self, path):
        logging.info("Loading question from path: %s", path)

        fd = file(path, "r")
        self._load_descriptor(fd, path)

    def load_directory(self, directory):
        logging.info("Loading questions from directory: %s", directory)
        for name in [name for name in os.listdir(directory)
                     if name.endswith(".txt")]:
            path = os.path.join(directory, name)
            self.load_path(path)


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

    required_fields = ["name", "description"]
    optional_fields = {
        "architectures": ALL_ARCHITECTURES,
        "categories": ALL_CATEGORIES,
        "depends": [],
        "command": None,
        "optional": False}

    def __init__(self, **kwargs):
        self.properties = kwargs
        self.answer = None
        self._validate()

    def get_properties(self):
        return dict((f, self.properties[f]) \
            for f in Question.required_fields + Question.optional_fields.keys())

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

    def __str__(self):
        return self.name

    def __getattr__(self, attr):
        if attr in self.properties:
            return self.properties[attr]

        raise AttributeError, attr

    def set_answer(self, status, data='', auto=False):
        self.answer = Answer(self, status, data, auto)
