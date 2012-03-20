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
import time
from gi.repository import GObject

from gettext import gettext as _
from string import Template

from checkbox.user_interface import (UserInterface,
    NEXT, PREV, YES_ANSWER, NO_ANSWER, SKIP_ANSWER,
    ANSWER_TO_STATUS)
import dbus
from dbus.mainloop.glib import DBusGMainLoop

ANSWER_TO_OPTION = {
    YES_ANSWER: _('yes'),
    NO_ANSWER: _('no'),
    SKIP_ANSWER: _('skip')}

OPTION_TO_ANSWER = dict((o, a)
                        for a, o in ANSWER_TO_OPTION.items())


class QTInterface(UserInterface):
    def __init__(self, title, data_path):
        super(QTInterface, self).__init__(title, data_path)
        self._app_title = title
        notReady = True
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

    def onClosedFrontend(self):
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

        self.qtiface.showText(text)
        self.wait_on_signals(fullTestsClicked=onFullTestsClicked)

    def show_entry(self, text, value, previous=None, next=None):
        def onSubmitTestsClicked():
            self.loop.quit()

        self.qtiface.showEntry(text)
        self.wait_on_signals(submitTestsClicked=onSubmitTestsClicked)
        return self.qtiface.getEmailAddress()

    def show_check(self, text, options=[], default=[]):
        return False

    def show_radio(self, text, options=[], default=None):
        return False

    def show_tree(self, text, options={}, default={}):
        indexedOptions = {}

        def onStartTestsClicked():
            self.direction = NEXT
            self.loop.quit()

        def buildBranch(options, baseIndex="1"):
            internalIndex = 1
            for test, state in options.iteritems():
                if isinstance(state, dict):
                    indexedOptions[
                        baseIndex + "." + str(internalIndex)] = {test: ''}
                    buildBranch(state, baseIndex + "." + str(internalIndex))
                else:
                    indexedOptions[
                        baseIndex + "." + str(internalIndex)] = {test: state}
                internalIndex += 1

        def buildDict(options, baseIndex="1"):
            internalIndex = 1
            branch = {}
            while True:
                currentIndex = baseIndex + "." + str(internalIndex)
                if currentIndex in options:
                    key = options[currentIndex].keys()[0]
                    value = options[currentIndex].values()[0]
                    if value == "menu":
                        branch[key] = buildDict(options, currentIndex)
                    else:
                        branch[key] = value
                    internalIndex += 1
                else:
                    break
            return branch

        self._set_main_title()
        buildBranch(options)

        self.qtiface.showTree(text, indexedOptions)
        self.wait_on_signals(
            startTestsClicked=onStartTestsClicked)

        return buildDict(self.qtiface.getTestsToRun())

    def _run_test(self, test, runner):
        (status, data, duration) = runner(test)

        return Template(test["info"]).substitute({
            "output": data.strip()})

    def show_test(self, test, runner):
        def onStartTestClicked():
            self._run_test(test, runner)

        def onNextTestClicked():
            test["status"] = ANSWER_TO_STATUS[SKIP_ANSWER]
            self.direction = NEXT
            self.loop.quit()

        def onPreviousTestClicked():
            self.direction = PREV
            self.loop.quit()

        def onYesTestClicked():
            test["status"] = ANSWER_TO_STATUS[YES_ANSWER]
            self.direction = NEXT
            self.loop.quit()

        def onNoTestClicked():
            test["status"] = ANSWER_TO_STATUS[NO_ANSWER]
            self.direction = NEXT
            self.loop.quit()

        enableTestButton = True
        self._set_main_title(test["name"])
        if test["info"] and "$output" in test["info"]:
            info = self._run_test(test, runner)
            enableTestButton = False
        else:
            info = ""

        self.qtiface.showTest(
            test["purpose"], test["steps"], test["verification"], info,
            test["suite"], test["name"], enableTestButton)
        self.wait_on_signals(
            startTestClicked=onStartTestClicked,
            nextTestClicked=onNextTestClicked,
            previousTestClicked=onPreviousTestClicked,
            noTestClicked=onNoTestClicked,
            yesTestClicked=onYesTestClicked)

        test["data"] = ""
        return False

    def show_info(self, text, options=[], default=None):
        return self.qtiface.showInfo(text, options, default)

    def show_error(self, text):
        self.qtiface.showError(text)

    def update_status(self, job):
        if 'type' in job and job["type"] == "test":
            self.qtiface.updateAutoTestStatus(job["status"], job["name"])

    def wait_on_signals(self, **signals):
        for name, function in signals.iteritems():
            self.bus.add_signal_receiver(function, name)

        self.loop.run()
        if self.direction == KeyboardInterrupt:
            raise KeyboardInterrupt

        for name, function in signals.iteritems():
            self.bus.remove_signal_receiver(function, name)
