import unittest

from hwtest.config import Config


class TestHelper(unittest.TestCase):

    config_path = "./examples/hwtest.conf"
    config_section = "hwtest/registries"

    def setUp(self):
        section_test_class_name = self.__class__.__name__
        section_class_name = section_test_class_name.replace("Test", "")
        section_name = section_class_name.replace("Registry", "").lower()

        config = Config(self.config_path)
        self.config = config.get_section("%s/%s" \
            % (self.config_section, section_name))
