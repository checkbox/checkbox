#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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
from gettext import gettext as _

from checkbox.job import FAIL
from checkbox.plugin import Plugin
from checkbox.reactor import StopAllException
from checkbox.registry import registry_eval_recursive

class DummyUserInterface:
    pass

try:
    from apport.ui import UserInterface
    from apport.crashdb import get_crashdb
except:
    UserInterface = DummyUserInterface


CATEGORY_TO_PACKAGE = {
    "VIDEO": "xorg",
    "SOUND": "alsa-base"}

CATEGORY_TO_SYMPTOM = {
    "DISK":  "storage"}


class ApportOptions(object):

    def __init__(self, test, package, symptom):
        self.test = test
        self.package = package
        self.symptom = symptom
        self.pid = None


class ApportUserInterface(UserInterface):

    def __init__(self, interface, options):
        self.interface = interface
        self.options = options
        self.report = None
        self.report_file = None
        self.cur_package = None

        # ImportError raised during package upgrade
        self.crashdb = get_crashdb(None)

    def ui_info_message(self, title, text):
        self.interface.show_info(text, ["close"])

    def ui_error_message(self, title, text):
        self.interface.show_progress_stop()
        self.interface.show_error(text)

    def ui_start_info_collection_progress(self):
        self.interface.show_progress_start(
            _("Collecting information about this test.\n"
              "This might take a few minutes."))

    def ui_pulse_info_collection_progress(self):
        self.interface.show_progress_pulse()

    def ui_stop_info_collection_progress(self):
        # tags
        self.report.setdefault("Tags", "")
        if self.report["Tags"]:
            self.report["Tags"] += " "

        self.report["Tags"] += "checkbox-bug"

        # checkbox
        test = self.options.test
        self.report["CheckboxTest"] = test["name"]
        if test.get("description"):
            self.report["CheckboxDescription"] = test["description"]
        if test.get("data"):
            self.report["CheckboxData"] = test["data"]
        if test.get("command"):
            self.report["CheckboxCommand"] = test["command"]
        if test.get("environ"):
            self.report["CheckboxEnvironment"] = test["environ"]

        self.interface.show_progress_stop()

    def ui_start_upload_progress(self):
        self.interface.show_progress_start(
            _("Collected information is being sent for bug tracking.\n"
            "This might take a few minutes."))

    def ui_set_upload_progress(self, progress):
        self.interface.show_progress_pulse()

    def ui_stop_upload_progress(self):
        self.interface.show_progress_stop()

    def ui_present_report_details(self):
        return "full"

    def ui_question_choice(self, text, options, multiple):
        self.interface.show_progress_stop()

        if multiple:
            results = self.interface.show_check(text, options)
        else:
            results = [self.interface.show_radio(text, options)]

        return [options.index(r) for r in results]

    def open_url(self, url):
        self.interface.show_url(url)


class ApportPrompt(Plugin):

    def register(self, manager):
        super(ApportPrompt, self).register(manager)

        if isinstance(ApportUserInterface, DummyUserInterface):
            return

        self._manager.reactor.call_on("prompt-test", self.prompt_test, 100)

    def prompt_test(self, interface, test):
        if test["status"] != FAIL:
            return

        package = None
        symptom = None

        # Give lowest priority to required packages
        for require in test.get("requires", []):
            packages = registry_eval_recursive(self._manager.registry.packages,
                require)
            if packages:
                package = packages[0].name
                break

        # Give highest priority to required devices
        for require in test.get("requires", []):
            devices = registry_eval_recursive(self._manager.registry.udev,
                require)
            for device in devices:
                if device.category in CATEGORY_TO_PACKAGE:
                    package = CATEGORY_TO_PACKAGE[device.category]
                    break

                if device.category in CATEGORY_TO_SYMPTOM:
                    symptom = CATEGORY_TO_SYMPTOM[device.category]
                    break

        # Do not report a bug if no package nor symptom is defined
        if not package and not symptom:
            return

        response = interface.show_info("Do you want to report a bug?",
            ["yes", "no"], "no")
        if response == "no":
            return

        try:
            options = ApportOptions(test, package, symptom)
            apport_interface = ApportUserInterface(interface, options)
        except ImportError, e:
            interface.show_error("Is a package upgrade in process? Error: %s" % e)
            return

        try:
            if symptom and hasattr(apport_interface, "run_symptom"):
                apport_interface.run_symptom()
            else:
                apport_interface.run_report_bug()
        except SystemExit, e:
            # In case of error, show_error already have been called
            raise StopAllException


factory = ApportPrompt
