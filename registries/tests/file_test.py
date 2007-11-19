import sys
import unittest

sys.path.insert(0, "registries")
from file import FileRegistry


class FileRegistryTest(unittest.TestCase):

    def test_file(self):
        registry = FileRegistry(None, "test")
        self.assertTrue(str(registry) is not None)
        self.assertTrue(len(str(registry)) > 0)
