import unittest

from hwtest.config import Config


class TestHelper(unittest.TestCase):

    def setUp(self):
        section_test_class_name = self.__class__.__name__
        section_class_name = section_test_class_name.replace("Test", "")
        section_name = section_class_name.replace("Registry", "").lower()

        config = Config()
        config.load_path("./examples/hwtest.conf")
        self.config = config.get_section("hwtest/registries/%s" % section_name)
