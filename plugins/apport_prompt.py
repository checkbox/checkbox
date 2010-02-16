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
from subprocess import Popen, PIPE

from gettext import gettext as _

from checkbox.job import FAIL
from checkbox.plugin import Plugin
from checkbox.properties import Bool, Path, String
from checkbox.reactor import StopAllException


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

    def __init__(self, test, device, package, symptom):
        self.test = test
        self.device = device
        self.package = package
        self.symptom = symptom
        self.pid = None
        self.save = False


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
        if "Tags" in self.report:
            tags = self.report["Tags"].split(" ")
        else:
            tags = []

        tags.append("checkbox-bug")
        if self.options.device:
            tags.append(self.options.device)

        self.report["Tags"] = " ".join(tags)

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

    def ui_present_report_details(self, *args):
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

    # Default configuration filename
    default_filename = Path(default="/etc/default/apport")

    # Default enabled state
    default_enabled = Bool(required=False)

    # Default package if none is detected
    default_package = String(required=False)

    def register(self, manager):
        super(ApportPrompt, self).register(manager)

        if isinstance(ApportUserInterface, DummyUserInterface):
            return

        self._manager.reactor.call_on("gather", self.gather)
        self._manager.reactor.call_on("prompt-test", self.prompt_test, 100)

    def gather(self):
        if self.default_enabled is None:
            value = Popen("unset enabled && . %s && echo ${enabled}"
                % self.default_filename,
                shell=True, stdout=PIPE, stderr=PIPE).communicate()[0]
            self.default_enabled = value.strip() == "1"

    def prompt_test(self, interface, test):
        if not self.default_enabled:
            return

        if test["status"] != FAIL:
            return

        device = None
        package = None
        symptom = None

        # Give lowest priority to required packages
        for resource in test.get("resources", []):
            if resource["suite"] == "package":
                package = resource["name"]
                break

        # Give highest priority to required devices
        for resource in test.get("resources", []):
            if resource["suite"] == "device":
                category = resource["category"]
                if category in CATEGORY_TO_PACKAGE:
                    package = CATEGORY_TO_PACKAGE[category]
                    break

                if category in CATEGORY_TO_SYMPTOM:
                    symptom = CATEGORY_TO_SYMPTOM[category]
                    break

        # Default to configuration
        if not package:
            package = self.default_package

        # Do not report a bug if no package nor symptom is defined
        if not package and not symptom:
            return

        response = interface.show_info(_("Do you want to report a bug?"),
            ["yes", "no"], "no")
        if response == "no":
            return

        # Determine corresponding device
        for resource in test.get("resources", []):
            if resource["suite"] == "device":
                device = resource["category"].lower()
                break

        try:
            options = ApportOptions(test, device, package, symptom)
            apport_interface = ApportUserInterface(interface, options)
        except ImportError, e:
            interface.show_error(_("Is a package upgrade in process? Error: %s") % e)
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
