import os
import types
import unittest

import hwtest.constants

hwtest.constants.SHARE_DIR = os.curdir

from hwtest.action import Action, execute


class ActionTest(unittest.TestCase):

    def test_cpu_info(self):
        cpu_info = execute("cpu_info")
        self.assertTrue(type(cpu_info) is types.StringType)

    def test_dmesg_nic(self):
        dmesg_nic = execute("dmesg_nic")
        self.assertTrue(type(dmesg_nic) is types.StringType)
