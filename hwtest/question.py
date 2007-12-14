"""
The purpose of a question is to encapsulate the concept of a test
which might be presented in several ways. For example, a question might
require manual intervention whereas another question might be completely
automatic. Either way, this module provides the base common to each type
of question.
"""

import re
import os
import logging
from subprocess import Popen, PIPE

from hwtest.excluder import Excluder
from hwtest.iterator import Iterator
from hwtest.repeater import PreRepeater
from hwtest.resolver import Resolver
from hwtest.answer import Answer, NO, SKIP

from hwtest.lib.environ import add_variable, remove_variable


DESKTOP = 'desktop'
LAPTOP = 'laptop'
SERVER = 'server'
ALL_CATEGORIES = [DESKTOP, LAPTOP, SERVER]

I386 = 'i386'
AMD64 = 'amd64'
SPARC = 'sparc'
ALL_ARCHITECTURES = [I386, AMD64, SPARC]


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

    required_fields = ["name", "type", "description", "suite"]
    optional_fields = {
        "architectures": ALL_ARCHITECTURES,
        "categories": ALL_CATEGORIES,
        "depends": [],
        "relations": [],
        "requires": None,
        "command": None,
        "optional": False}

    def __init__(self, registry, **kwargs):
        self.registry = registry
        self.properties = kwargs
        self.answer = None
        self._cache = {}
        self._validate()

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

    def run(self):
        self.run_command()
        self.run_description()
        return self._output

    def run_command(self):
        if self.command:
            logging.info("Running command: %s" % self.command)
            process = Popen([self.command], shell=True,
                stdin=None, stdout=PIPE, stderr=PIPE,
                close_fds=True)
            (stdout, stderr) = process.communicate()
            self._output = (stdout, stderr, process.wait())
        else:
            self._output = ('', '', 0)

        return self._output

    def run_description(self):
        if not hasattr(self, "_description"):
            self._description = self.properties["description"]
        add_variable("output", self._output[0])
        command = "cat <<EOF\n%s\nEOF\n" % self._description
        self.properties["description"] = os.popen(command).read()
        remove_variable("output")
        return self.properties["description"]

    def get_properties(self):
        properties = {}
        for field in Question.required_fields + Question.optional_fields.keys():
            properties[field] = self.properties[field]
        if self.answer:
            properties['answer'] = self.answer.get_properties()
        return properties

    def set_answer(self, status, data='', auto=False):
        self.answer = Answer(self, status, data, auto)
