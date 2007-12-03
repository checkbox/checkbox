import sys
import unittest

sys.path.insert(0, "registries")
from command import CommandRegistry


class CommandRegistryTest(unittest.TestCase):

    def test_command(self):
        registry = CommandRegistry(None, "echo -n foo")
        self.assertTrue(str(registry) is not None)
        self.assertTrue(str(registry) == "foo")
