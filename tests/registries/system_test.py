import re
import sys
import unittest

sys.path.insert(0, "registries")
from system import SystemRegistry


class SystemRegistryTest(unittest.TestCase):

    def test_id(self):
        registry = SystemRegistry(None)
        self.assertTrue(registry.id)
        self.assertTrue(re.search(r"^[\w]+$", registry.id))
