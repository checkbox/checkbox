# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

"""Ubuntu Touch App autopilot tests."""

import os

from autopilot import input, platform
from autopilot.exceptions import StateNotFoundError
from autopilot.introspection.dbus import StateNotFoundError
from autopilot.matchers import Eventually
from testtools.matchers import Equals
from ubuntuuitoolkit import base, emulators


def _get_module_include_path():
    return os.path.join(get_path_to_source_root(), 'modules')


def get_path_to_source_root():
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__), '..', '..', '..', '..'))


class ClickAppTestCase(base.UbuntuUIToolkitAppTestCase):
    """Common test case that provides several useful methods for the tests."""

    package_id = 'com.ubuntu.checkbox'
    app_name = 'checkbox-converged-autopilot'

    launcher = ''

    def setUp(self):
        super(ClickAppTestCase, self).setUp()
        self.pointing_device = input.Pointer(self.input_device_class.create())
        if self.launcher:
            link = '/tmp/checkbox_autopilot_launcher'
            target = os.path.abspath(os.path.join('launchers', self.launcher))
            if os.path.lexists(link):
                os.unlink(link)
            os.symlink(target, link)
        self.launch_application()
        self.assertThat(self.main_view.visible, Eventually(Equals(True)))

    def tearDown(self):
        if self.launcher:
            os.unlink('/tmp/checkbox_autopilot_launcher')
        super(ClickAppTestCase, self).tearDown()

    def skipResumeIfShown(self):
        """Skip restart screen if presented."""
        # this doesn't use 'long wait' helper, because a 'welcome page' may be
        # displayed and autopilot would take 5*timeout to figure it out
        retries = 5
        while retries > 0:
            try:
                resume_page = self.app.wait_select_single(
                    objectName='resumeSessionPage', visible=True)
                restart_btn = resume_page.wait_select_single(
                    objectName='restartButton', visible=True)
                self.pointing_device.click_object(restart_btn)
                return
            except StateNotFoundError:
                pass
            try:
                self.app.wait_select_single(
                    objectName='welcomePage', visible=True)
                return
            except StateNotFoundError:
                pass

    def start_and_select_tests(self, category_id, job_ids):
        self.skipResumeIfShown()
        welcome_page = self.long_wait_select_single(
            self.app, objectName='welcomePage', state='loaded')
        start_btn = welcome_page.wait_select_single(
            objectName='startTestButton')
        self.pointing_device.click_object(start_btn)
        tp_selection_page = self.app.wait_select_single(
            objectName='testplanSelectionPage', visible=True)
        tp_item = tp_selection_page.wait_select_single(
            objectName='listItem', item_mod_id=(
                '2015.com.canonical.certification::checkbox-converged-autopilot'))
        self.pointing_device.click_object(tp_item)
        continue_btn = tp_selection_page.wait_select_single(
            objectName='continueButton', visible=True)
        self.pointing_device.click_object(continue_btn)
        category_page = self.app.wait_select_single(
            objectName='categorySelectionPage', visible=True)
        self._click_action_button('trailingActionBar', 'toggleSelectionAction')
        list_item = category_page.wait_select_single(
            objectName='listItem', item_mod_id=category_id)
        self.pointing_device.click_object(list_item)
        continue_btn = category_page.wait_select_single(
            objectName='continueButton', visible=True)
        self.pointing_device.click_object(continue_btn)
        test_selection_page = self.app.wait_select_single(
            objectName='testSelectionPage', visible=True)
        self._click_action_button('trailingActionBar', 'toggleSelectionAction')
        # lists are built dynamically, so there is a chance that proxies for
        # qml objects for list items that are down below are not yet present.
        # To make sure everything is loaded and ready, scroll to the bottom
        list_view = self.app.wait_select_single(
            objectName='listView', visible=True)
        for job_id in job_ids:
            found = False
            while not found:
                try:
                    list_item = test_selection_page.select_single(
                        objectName='listItem', item_mod_id=job_id)
                    found = True
                    list_item.swipe_into_view()
                    self.pointing_device.click_object(list_item)
                except StateNotFoundError:
                    list_view.swipe_to_show_more_below()
        continue_btn = test_selection_page.wait_select_single(
            objectName='continueButton')
        self.pointing_device.click_object(continue_btn)

    def select_two_tests_and_quit(self):
        self.start_and_select_tests(
            '2015.com.canonical.certification::normal', [
                '2015.com.canonical.certification::autopilot/user-verify-1',
                '2015.com.canonical.certification::autopilot/user-verify-2'])
        # make sure that test is shown (therefore session has been started)
        self.app.wait_select_single(
            objectName='userInteractVerifyIntroPage', visible=True)
        self.terminate()

    def process_sequence_of_clicks_on_pages(self, steps):
        """
        Do a sequence of clicks on simple page->component hierarchies.

        :param steps:
            sequence of (page-objectName, component-objectName) pairs to go
            through.

        Typical run of checkbox-converged requires user to go through a sequence of
        pages that have pass/fail buttons on them. This function helps go
        through a sequence like that.
        """
        for parent, component in steps:
            self.app.wait_select_single(
                objectName=parent, visible=True)
            clickable = self.main_view.wait_select_single(
                objectName=component, visible=True)
            self.pointing_device.click_object(clickable)

    def check_results(self, results):
        results_page = self.app.wait_select_single(
            objectName='resultsPage', visible=True)
        lbl_passed = results_page.wait_select_single(objectName='passedLabel')
        self.assertThat(lbl_passed.text.startswith(results['passed']),
                        Equals(True))
        lbl_failed = results_page.wait_select_single(objectName='failedLabel')
        self.assertThat(lbl_failed.text.startswith(results['failed']),
                        Equals(True))
        lbl_skipped = results_page.wait_select_single(
            objectName='skippedLabel')
        self.assertThat(lbl_skipped.text.startswith(results['skipped']),
                        Equals(True))

    def launch_application(self):
        if platform.model() == 'Desktop':
            self._launch_application_from_desktop()
        else:
            self._launch_application_from_phablet()

    def long_wait_select_single(self, target, *args, **kwargs):
        """Try multiple times to do wait_select_single on target."""
        retries = 5
        while retries > 0:
            try:
                return getattr(target, 'wait_select_single')(*args, **kwargs)
            except StateNotFoundError:
                retries -= 1
                continue
        raise StateNotFoundError(*args, **kwargs)

    def terminate(self):
        if platform.model() == 'Desktop':
            self.app.process.terminate()
        else:
            import subprocess
            subprocess.call(['pkill', 'qmlscene'])

    def _launch_application_from_desktop(self):
        app_qml_source_location = self._get_app_qml_source_path()
        if os.path.exists(app_qml_source_location):
            self.app = self.launch_test_application(
                base.get_qmlscene_launch_command(),
                '-I', _get_module_include_path(),
                '-I', self._get_plainbox_qml_modules_path(),
                app_qml_source_location,
                '--autopilot',
                '--settings=""',
                '--launcher=/tmp/checkbox_autopilot_launcher',
                app_type='qt',
                emulator_base=emulators.UbuntuUIToolkitEmulatorBase)
        else:
            raise NotImplementedError(
                "On desktop we can't install click packages yet, so we can "
                "only run from source.")

    def _get_app_qml_source_path(self):
        return os.path.join(
            self._get_path_to_app_source(), 'checkbox-converged.qml')

    def _get_path_to_app_source(self):
        return os.path.join(get_path_to_source_root(), 'checkbox-touch')

    def _get_plainbox_qml_modules_path(self):
        try:
            from plainbox.impl import get_plainbox_dir
            return os.path.join(get_plainbox_dir(), 'data', 'plainbox-qml-modules')
        except ImportError:
            return os.path.join(self._get_path_to_app_source(), 'lib', 'py',
                                'plainbox', 'data', 'plainbox-qml-modules')

    def _click_action_button(self, bar_name, actionName):
        action_bar = self.app.wait_select_single(
            objectName=bar_name, visible=True)
        action_bar.click_action_button(actionName)

    def _launch_application_from_phablet(self):
        # On phablet, we only run the tests against the installed click
        # package.
        self.app = self.launch_click_package(
            self.package_id,
            self.app_name,
            emulator_base=emulators.UbuntuUIToolkitEmulatorBase)

    @property
    def main_view(self):
        return self.app.select_single(emulators.MainView)
