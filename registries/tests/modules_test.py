from registries.modules import ModulesRegistry
from registries.tests.helpers import TestHelper


class ModulesRegistryTest(TestHelper):

    def setUp(self):
        super(ModulesRegistryTest, self).setUp()
        self.registry = ModulesRegistry(self.config, "registries/tests/modules_test.txt")

    def test_name(self):
        self.assertTrue(self.registry["ieee80211_crypt_ccmp"] is not None)

    def test_size(self):
        self.assertTrue(self.registry["ieee80211_crypt_ccmp"]["size"] == 7552)
        self.assertTrue(self.registry["freq_table"]["size"] == 4740)

    def test_instances(self):
        self.assertTrue(self.registry["ieee80211_crypt_ccmp"]["instances"] == 3)
        self.assertTrue(self.registry["freq_table"]["instances"] == 2)

    def test_dependencies(self):
        self.assertTrue(len(self.registry["ieee80211_crypt_ccmp"]["dependencies"]) == 0)
        self.assertTrue(len(self.registry["freq_table"]["dependencies"]) == 2)
        self.assertTrue("speedstep_centrino" in self.registry["freq_table"]["dependencies"])
        self.assertTrue("cpufreq_stats" in self.registry["freq_table"]["dependencies"])

    def test_state(self):
        self.assertTrue(self.registry["ieee80211_crypt_ccmp"]["state"] == "Live")
        self.assertTrue(self.registry["freq_table"]["state"] == "Live")

    def test_offset(self):
        self.assertTrue(self.registry["ieee80211_crypt_ccmp"]["offset"] == 4033564672)
        self.assertTrue(self.registry["freq_table"]["offset"] == int('0xf0528000', 16))

