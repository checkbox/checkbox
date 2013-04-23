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
import re
import time
from gi.repository import GObject

from gettext import gettext as _
from string import Template

from checkbox.job import PASS
from checkbox.user_interface import (UserInterface,
    NEXT, PREV, YES_ANSWER, NO_ANSWER, SKIP_ANSWER,
    ANSWER_TO_STATUS)
import dbus
from dbus.mainloop.glib import DBusGMainLoop

ANSWER_TO_OPTION = {
    YES_ANSWER: 'yes',
    NO_ANSWER: 'no',
    SKIP_ANSWER: 'skip'}

OPTION_TO_ANSWER = dict((o, a)
                        for a, o in ANSWER_TO_OPTION.items())
def dummy_handle_reply(r=None):
    return

def dummy_handle_error(e=None):
    return

class QTInterface(UserInterface):
    def __init__(self, title, data_path):
        super(QTInterface, self).__init__(title, data_path)
        self._app_title = title
        notReady = True
        infoResult = None
        while notReady:
            try:
                self.bus = dbus.SessionBus(mainloop=DBusGMainLoop())
                self.qtfront = self.bus.get_object(
                    'com.canonical.QtCheckbox', '/QtCheckbox')
                self.qtiface = dbus.Interface(
                    self.qtfront, dbus_interface='com.canonical.QtCheckbox')
                self.loop = GObject.MainLoop()
                notReady = False
            except:
                time.sleep(0.5)
        self.bus.add_signal_receiver(
            self.onClosedFrontend, "closedFrontend")
        self.bus.add_signal_receiver(
            self.onReviewTestsClicked, "reviewTestsClicked")
        self.qtiface.setInitialState()

        self._set_main_title()

    def onReviewTestsClicked(self):
        self.show_url(self.report_url)

    def onClosedFrontend(self, finished):
        if bool(finished):
            self.direction = NEXT
        else:
            self.direction = KeyboardInterrupt
        self.loop.quit()

    def _set_main_title(self, test_name=None):
        title = self._app_title
        if test_name:
            title += " - %s" % test_name
        self.qtiface.setWindowTitle(title)

    def show_progress_start(self, message):
        self.qtiface.startProgressBar(message)

    def show_progress_stop(self):
        self.qtiface.stopProgressBar()

    def show_progress_pulse(self):
        # not used if we have a main event loop
        pass

    def show_text(self, text, previous=None, next=None):
        def onFullTestsClicked():
            self.direction = NEXT
            self.loop.quit()

        def onCustomTestsClicked():
            self.loop.quit()

        #Reset window title
        self._set_main_title()

        if not self.ui_flags == {}:
            self.qtiface.setUiFlags(self.ui_flags)

        self.qtiface.showText(text)
        self.wait_on_signals(fullTestsClicked=onFullTestsClicked)

    def show_entry(self, text, value, label='', submitToHexr=False, previous=None, next=None):
        def onSubmitTestsClicked():
            self.loop.quit()

        # Replace links wiki style markup with html markup
        text = '<html>{}</html>'.format(text)
        text = text.replace('\n', '<br/>')
        text = re.sub(r'\[\[([^|]*)\|([^\]]*)\]\]',
                      lambda m: '<a href="{}">{}</a>'
                                .format(m.group(1), m.group(2)),
                      text)

        # Make sure that value is a string
        if value is None:
            value = ''

        self.qtiface.showEntry(text, value, label, submitToHexr)
        self.wait_on_signals(submitTestsClicked=onSubmitTestsClicked)
        return self.qtiface.getSubmissionData()

    def show_check(self, text, options=[], default=[]):
        return False

    def show_radio(self, text, options=[], default=None):
        return False

    def show_tree(self, text, options={}, default={}, deselect_warning=""):
        indexedOptions = {}
        indexedDefaults = {}

        def onStartTestsClicked():
            self.direction = NEXT
            self.loop.quit()

        def buildBranch(options, default, baseIndex="1"):
            internalIndex = 1
            for test, state in options.items():
                active = test in default
                if isinstance(state, dict):
                    indexedOptions[
                        baseIndex + "." + str(internalIndex)] = {test: ''}
                    indexedDefaults[
                        baseIndex + "." + str(internalIndex)] = {test: active}
                    buildBranch(state, default.get(test, {}), baseIndex + "." + str(internalIndex))
                else:
                    indexedOptions[
                        baseIndex + "." + str(internalIndex)] = {test: state}
                    indexedDefaults[
                        baseIndex + "." + str(internalIndex)] = {test: active}
                internalIndex += 1

        def buildDict(options, baseIndex="1"):
            internalIndex = 1
            branch = {}
            while True:
                currentIndex = baseIndex + "." + str(internalIndex)
                if currentIndex in options:
                    key = list(options[currentIndex].keys())[0]
                    value = list(options[currentIndex].values())[0]
                    if value == "menu":
                        branch[key] = buildDict(options, currentIndex)
                    else:
                        branch[key] = value
                    internalIndex += 1
                else:
                    break
            return branch

        self._set_main_title()
        buildBranch(options, default)

        self.qtiface.showTree(text, indexedOptions, indexedDefaults,
                              deselect_warning)
        self.wait_on_signals(
            startTestsClicked=onStartTestsClicked)

        return buildDict(self.qtiface.getTestsToRun())

    def _run_test(self, test, runner):
        self.qtiface.showTestControls(False)
        (status, data, duration) = runner(test)
        self.qtiface.setTestResult(True if status == PASS else False)
        self.qtiface.showTestControls(True)

        if test["info"]:
            info = Template(test["info"]).substitute({"output": data.strip()})
        else:
            info = ""

        return info

    def show_test(self, test, runner):
        def onStartTestClicked():
            self._run_test(test, runner)

        def onNextTestClicked():
            #Get response from UI
            answer = self.qtiface.getTestResult()
            test["status"] = ANSWER_TO_STATUS[answer]
            self.direction = NEXT
            self.loop.quit()

        def onPreviousTestClicked():
            self.direction = PREV
            self.loop.quit()

        enableTestButton = False
        self._set_main_title(test["name"])
        if test["info"] and "$output" in test["info"]:
            info = self._run_test(test, runner)
        else:
            info = ""

        if not "data" in test:
            test["data"] = ""
        if "command" in test:
            enableTestButton = True

        #If we were in progress, stop showing that now, as we're 
        #awaiting user interaction
        self.show_progress_stop()

        self.qtiface.showTest(
            test["purpose"], test["steps"], test["verification"], info, test["data"],
            test["suite"], test["name"], enableTestButton)
        self.wait_on_signals(
            startTestClicked=onStartTestClicked,
            nextTestClicked=onNextTestClicked,
            previousTestClicked=onPreviousTestClicked)

        test["data"] = self.qtiface.getTestComment()
        #Unset the title, since we finished the job
        self._set_main_title()
        return False

    def show_info(self, text, options=[], default=None):
        def onInfoBoxResult(result):
            #result here will always be a dbus String
            #it may not be convertable with str due to the fact that it
            #may contain non-ascii characters, so we need to convert to
            #internal Python unicode instead.
            self.infoResult = str(result)
            self.loop.quit()

        self.qtiface.showInfo(
            text, options, default,
            reply_handler=dummy_handle_reply,
            error_handler=dummy_handle_error)
        self.wait_on_signals(
            infoBoxResult=onInfoBoxResult)
        return self.infoResult

    def show_error(self, primary_text,
                   secondary_text=None, detailed_text=None):
        def onErrorBoxClosed():
            self.loop.quit()

        if secondary_text == None:
            secondary_text = ""
        if detailed_text == None:
            detailed_text = ""

        self.qtiface.showError(str(primary_text),
                str(secondary_text), str(detailed_text),
                reply_handler=dummy_handle_reply,
                error_handler=dummy_handle_error)
        self.wait_on_signals(
            errorBoxClosed=onErrorBoxClosed)

    def update_status(self, job):
        if 'type' in job and job["type"] == "test":
            self.qtiface.updateAutoTestStatus(job["status"], job["name"])
       
        self.show_progress_start(_("Working"))

    def wait_on_signals(self, **signals):
        for name, function in signals.items():
            self.bus.add_signal_receiver(function, name)

        self.loop.run()
        if self.direction == KeyboardInterrupt:
            raise KeyboardInterrupt

        for name, function in signals.items():
            self.bus.remove_signal_receiver(function, name)
