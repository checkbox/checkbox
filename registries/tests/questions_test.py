import re
import sys
import unittest

sys.path.insert(0, "registries")
from question import QuestionsRegistry


class QuestionsRegistryTest(unittest.TestCase):

    def test_name(self):
        registry = QuestionsRegistry(None)
