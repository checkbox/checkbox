#
# This file is part of Checkbox.
#
# Copyright 2012 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import os
import unittest
from checkbox.lib.path import path_expand_recursive
from checkbox.lib.template_i18n import TemplateI18n


class MessageFileFormatTest(unittest.TestCase):

    name = "message file format test"

    def read_jobs(self):
        messages = []
        if os.environ.get("CHECKBOX_PACKAGING", 0):
            jobs_path = "./build/share/checkbox/jobs"
        else:
            jobs_path = "./jobs"

        for filename in path_expand_recursive(jobs_path):
            if not filename.endswith("~"):
                file = open(filename, "r", encoding="utf-8")
                template = TemplateI18n()
                messages += template.load_file(file, filename)
        return messages

    def setUp(self):
        self.messages = self.read_jobs()

    def test_job_files_valid(self):
        messages = self.messages
        self.assertTrue(messages)
        self.assertTrue(len(messages) > 0)

    def test_all_messages_have_name(self):
        messages = self.messages
        for message in messages:
            self.assertIn("name", message)

    def test_all_messages_have_command_or_description(self):
        messages = self.messages
        for message in messages:
            self.assertTrue("command" in message or "description" in message)
