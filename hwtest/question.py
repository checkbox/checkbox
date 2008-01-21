"""
The purpose of a question is to encapsulate the concept of a test
which might be presented in several ways. For example, a question might
require manual intervention whereas another question might be completely
automatic. Either way, this module provides the base common to each type
of question.
"""

import re

from hwtest.excluder import Excluder
from hwtest.repeater import PreRepeater
from hwtest.resolver import Resolver
from hwtest.answer import Answer, NO, SKIP
from hwtest.command import Command
from hwtest.description import Description
from hwtest.iterator import Iterator, NEXT, PREV


DESKTOP = "desktop"
LAPTOP = "laptop"
SERVER = "server"
ALL_CATEGORIES = [DESKTOP, LAPTOP, SERVER]

I386 = "i386"
AMD64 = "amd64"
SPARC = "sparc"
ALL_ARCHITECTURES = [I386, AMD64, SPARC]


class QuestionManager(object):
    """
    Question manager which is essentially a container of questions.
    """

    def __init__(self):
        self._questions = []
        self._architecture = None
        self._category = None

    def add_question(self, question):
        """
        Add a question to the manager.
        """
        self._questions.append(question)

    def set_architecture(self, architecture):
        self._architecture = architecture

    def set_category(self, category):
        self._category = category

    def get_iterator(self, direction=NEXT):
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
                import pdb; pdb.set_trace()
                for dependent in resolver.get_dependents(question):
                    dependent.answer.status = SKIP

        def requires_exclude_func(question):
            """Excluder function which removes question when the requires
               field exists and doesn't meet the given requirements."""
            return isinstance(question.requires, list) \
                   and len(question.requires) == 0

        def architecture_exclude_func(question, architecture):
            """Excluder function which removes question when the architectures
               field exists and doesn't meet the given requirements."""
            return architecture and architecture not in question.architectures

        def category_exclude_func(question, category):
            """Excluder function which removes question when the categories
               field exists and doesn't meet the given requirements."""
            return category and category not in question.categories

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
            lambda question, architecture=self._architecture: \
                   architecture_exclude_func(question, architecture),
            lambda question, architecture=self._architecture: \
                   architecture_exclude_func(question, architecture))
        questions_iter = Excluder(questions_iter,
            lambda question, category=self._category: \
                   category_exclude_func(question, category),
            lambda question, category=self._category: \
                   category_exclude_func(question, category))

        if direction == PREV:
            while True:
                try:
                    questions_iter.next()
                except StopIteration:
                    break

        return questions_iter


class Question(object):
    """
    Question base class which should be inherited by each question
    implementation. A question instance contains the following required
    fields:

    name:          Unique name for a question.
    plugin:        Plugin name to handle this question.
    description:   Long description of what the question does.
    suite:         Name of the suite containing this question.

    An instance also contains the following optional fields:

    architectures: List of architectures for which this question is relevant:
                   amd64, i386, powerpc and/or sparc
    categories:    List of categories for which this question is relevant:
                   desktop, laptop and/or server
    depends:       List of names on which this question depends. So, if
                   the other question fails, this question will be skipped.
    relations:     Registry expression which points to the relations for this
                   question. For example: 'input.mouse' in info.capabilities
    requires:      Registry expression which is required to ask this
                   question. For example: lsb.release == '6.06'
    command:       Command to run for the question.
    optional:      Boolean expression set to True if this question is optional
                   or False if this question is required.
    """

    required_fields = ["name", "plugin", "description", "suite"]
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
        self.properties = self._validate(**kwargs)

    def _validate(self, **kwargs):
        # Unknown fields
        for field in kwargs.keys():
            if field not in self.required_fields + self.optional_fields.keys():
                raise Exception, \
                    "Question properties contains unknown field: %s" \
                    % field

        # Required fields
        for field in self.required_fields:
            if not kwargs.has_key(field):
                raise Exception, \
                    "Question properties does not contain '%s': %s" \
                    % (field, kwargs)

        # Typed fields
        for field in ["architectures", "categories", "depends"]:
            if kwargs.has_key(field):
                kwargs[field] = re.split(r"\s*,\s*", kwargs[field])

        # Eval fields
        for field in ["relations", "requires"]:
            if kwargs.has_key(field):
                kwargs[field] = self.registry.eval_recursive(kwargs[field])

        # Optional fields
        for field in self.optional_fields.keys():
            if not kwargs.has_key(field):
                kwargs[field] = self.optional_fields[field]

        # Command field
        kwargs["command"] = Command(kwargs.get("command"))

        # Description field
        kwargs["description"] = Description(kwargs["description"],
            variables={"question": self})

        # Answer field
        kwargs["answer"] = Answer()

        return kwargs

    def __getattr__(self, attr):
        if attr in self.properties:
            return self.properties[attr]

        raise AttributeError, attr
