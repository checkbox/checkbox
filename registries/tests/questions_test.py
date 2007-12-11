from registries.questions import QuestionsRegistry
from registries.tests.helpers import TestHelper


class QuestionsRegistryTest(TestHelper):

    def test_name(self):
        registry = QuestionsRegistry(self.config)
