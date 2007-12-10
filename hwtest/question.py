"""
The purpose of a question is to encapsulate the concept of a test
which might be presented in several ways. For example, a question might
require manual intervention whereas another question might be completely
automatic. Either way, this module provides the base common to each type
of question.
"""

import os
import re
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
    """
    Question parser which can take a string, a file or a directory. The
    content is parsed and the populates the 'questions' attributes of
    the parser.
    """

    def __init__(self):
        self.questions = []

    def _load_properties(self, **properties):
        if "name" not in properties:
            raise Exception, \
                "Question properties does not contain a 'name': %s" % properties

        logging.info("Loading question properties for: %s", properties["name"])

        if [q for q in self.questions if q["name"] == properties["name"]]:
            raise Exception, \
                "Question %s already has a question of the same name." \
                % properties["name"]

        self.questions.append(properties)

    def _load_descriptor(self, descriptor, name):
        for string in reader(descriptor):
            if not string:
                break

            properties = {}
            properties["suite"] = os.path.basename(name)

            def _save(field, value, extended, name):
                if value and extended:
                    raise Exception, \
                        "Path %s has both a value and an extended value." % name
                extended = extended.rstrip("\n")
                if field:
                    if properties.has_key(field):
                        raise Exception, \
                            "Path %s has a duplicate field '%s'" \
                            " with a new value '%s'." \
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

    def load_string(self, string):
        """
        Parse questions from given string.
        """
        logging.info("Loading question from string")
        descriptor = StringIO(string)
        self._load_descriptor(descriptor, "string")

    def load_path(self, path):
        """
        Parse questions from filename in given path.
        """
        logging.info("Loading question from path: %s", path)

        descriptor = file(path, "r")
        self._load_descriptor(descriptor, path)

    def load_directory(self, directory):
        """
        Parse questions from each filename in the given directory.
        """
        logging.info("Loading questions from directory: %s", directory)
        for name in [name for name in os.listdir(directory)
                     if name.endswith(".txt")]:
            path = os.path.join(directory, name)
            self.load_path(path)


class QuestionManager(object):
    """
    Question manager which is essentially a container of questions.
    """

    def __init__(self):
        self._questions = []

    def add_question(self, question):
        """
        Add a question to the manager.
        """
        self._questions.append(question)

    def get_iterator(self):
        """
        Get an iterator over the questions added to the manager. The
        purpose of this iterator is that it orders questions based on
        dependencies and enforces constraints defined in fields. For
        example, the requires field will be evaluated and the question
        will be skipped if this fails.
        """
        def dependent_prerepeat_func(question, resolver):
            """Pre repeater function which assigns the SKIP status to
               dependents when a question has a status of NO or SKIP."""
            answer = question.answer
            if answer and (answer.status == NO or answer.status == SKIP):
                for dependent in resolver.get_dependents(question):
                    dependent.set_answer(SKIP, auto=True)

        def requires_exclude_func(question):
            """Excluder function which removes question when the requires
               field exists and doesn't meet the given requirements."""
            return isinstance(question.requires, list) \
                   and len(question.requires) == 0

        def answered_exclude_next_func(question):
            """Excluder function which is called when clicking on the next
               button to skip questions which have been answered already."""
            return question.answer != None

        def answered_exclude_prev_func(question):
            """Excluder function which is called when clicking on the
               previous button when the question has been automatically
               answered."""
            if question.answer and question.answer.auto == True:
                question.answer = None
                return True
            else:
                return False

        resolver = Resolver()
        question_dict = dict((q.name, q) for q in self._questions)
        for question in self._questions:
            question_depends = [question_dict[d] for d in question.depends]
            resolver.add(question, *question_depends)

        questions = resolver.get_dependents()
        questions_iter = Iterator(questions)
        questions_iter = PreRepeater(questions_iter,
            lambda question, resolver=resolver: \
                   dependent_prerepeat_func(question, resolver))
        questions_iter = Excluder(questions_iter,
            requires_exclude_func, requires_exclude_func)
        questions_iter = Excluder(questions_iter,
            answered_exclude_next_func, answered_exclude_prev_func)

        return questions_iter


class Question(object):
    """
    Question base class which should be inherited by each question
    implementation. A question instance contains the following required
    fields:

    name:         Unique name for a question.
    description:  Long description of what the question does.
    suite:        Name of the suite containing this question.

    An instance also contains the following optional fields:

    architecture: List of architectures for which this question is relevant:
                  amd64, i386, powerpc and/or sparc
    categories:   List of categories for which this question is relevant:
                  desktop, laptop and/or server
    depends:      List of names on which this question depends. So, if
                  the other question fails, this question will be skipped.
    requires:     Registry expression which is required to ask this
                  question. For example: lsb.release == '6.06'
    relations:    Registry expression which points to the relations for this
                  question. For example: 'input.mouse' in info.capabilities
    command:      Command to run for the question.
    optional:     Boolean expression set to True if this question is optional
                  or False if this question is required.
    """

    required_fields = ["name", "description", "suite"]
    optional_fields = {
        "architectures": ALL_ARCHITECTURES,
        "categories": ALL_CATEGORIES,
        "depends": [],
        "requires": None,
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
        for field in Question.required_fields + Question.optional_fields.keys():
            properties[field] = self.properties[field]
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
                    % (field, self.properties)

        # Typed fields
        for field in ["architectures", "categories", "depends"]:
            if self.properties.has_key(field):
                self.properties[field] = re.split(r"\s*,\s*",
                    self.properties[field])

        # Eval fields
        for field in ["relations", "requires"]:
            if self.properties.has_key(field):
                self.properties[field] = self.registry.eval_recursive(
                    self.properties[field])

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
