import re

from hwtest.excluder import Excluder
from hwtest.iterator import Iterator
from hwtest.repeater import PreRepeater
from hwtest.resolver import Resolver

from hwtest.action import execute
from hwtest.plugin import Plugin
from hwtest.result import Result, FAIL, SKIP
from hwtest.template import convert_string


DESKTOP = 'desktop'
LAPTOP = 'laptop'
SERVER = 'server'
ALL_CATEGORIES = [DESKTOP, LAPTOP, SERVER]


class TestManager(object):
    def __init__(self, message_store):
        self.message_store = message_store
        self.tests = []

    def add(self, test):
        self.tests.append(test)

    def get_iterator(self):
        def repeat_func(test, resolver):
            result = test.result
            if result and (result.status == FAIL or result.status == SKIP):
                for dependent in resolver.get_dependents(test):
                    dependent.create_result(SKIP, auto=True)

        def exclude_next_func(test):
            return test.result != None

        def exclude_prev_func(test):
            if test.result and test.result.auto == True:
                test.result = None
                return True
            else:
                return False

        resolver = Resolver()
        test_dict = dict((test.name, test) for test in self.tests)
        for test in self.tests:
            test_deps = [test_dict[dep] for dep in test.deps]
            resolver.add(test, *test_deps)

        tests = resolver.get_dependents()
        tests_iter = Iterator(tests)
        repeater_iter = PreRepeater(tests_iter,
            lambda test, resolver=resolver: repeat_func(test, resolver))
        excluder_iter = Excluder(repeater_iter,
            exclude_next_func, exclude_prev_func)

        return excluder_iter


class Test(Plugin):

    def __init__(self, name, desc, deps=None, cats=None, optional=False):
        self.name = name
        self.desc = desc
        self.deps = deps and re.split('\s*,\s*', deps) or []
        self.cats = cats and re.split('\s*,\s*', cats) or ALL_CATEGORIES
        self.optional = optional
        self.result = None

    def __str__(self):
        return self.name
    
    @property
    def description(self):
        description = self.desc
        result = execute(self.name)
        if self.desc.find('$result') != -1:
            description = convert_string(self.desc, {'result': result})

        return description

    @property
    def categories(self):
        return self.cats

    def register(self, manager):
        self._manager = manager
        self._persist = self._manager.persist.root_at(self.name)
        self._manager.reactor.call_on("gather_information", self.gather_information)

    def create_message(self):
        message = {}
        message["type"] = "result-info"
        message["test-info"] = {
            "suite": "tool",
            "name": self.name,
            "description": self.description,
            "command": "",
            "architectures": [],
            "categories": self.categories,
            "optional": self.optional}
        if self.result:
            result = self.result
            message["result-info"] = {
                "status": result.status,
                "data": result.data}
        return message

    def gather_information(self):
        message = self.create_message()
        if len(message["result-info"]):
               self._manager.message_store.add(message)

    def create_result(self, status, data='', auto=False):
        self.result = Result(self, status, data, auto)
        return self.result
