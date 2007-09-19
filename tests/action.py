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

    def test_resolution_gutsy(self):
        contents = """
Screen 0: minimum 1024 x 768, current 1024 x 768, maximum 1024 x 768
default connected 1024x768+0+0 (normal left inverted right) 0mm x 0mm
   1024x768       60.0*"""
        resolution = execute("resolution", contents)
        self.assertEquals(resolution, "1024x768 @ 60 Hz")

    def test_resolution_dapper(self):
        contents = """
 SZ:    Pixels          Physical       Refresh
*0   1024 x 768    ( 347mm x 260mm )  *60
Current rotation - normal
Current reflection - none
Rotations possible - normal
Reflections possible - none"""
        resolution = execute("resolution", contents)
        self.assertEquals(resolution, "1024x768 @ 60 Hz")

