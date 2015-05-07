# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

"""Ubuntu Touch App autopilot tests."""

import os

from autopilot import input, platform
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

    package_id = ''  # TODO
    app_name = 'checkbox-touch'

    def setUp(self):
        super(ClickAppTestCase, self).setUp()
        self.pointing_device = input.Pointer(self.input_device_class.create())
        self.launch_application()
        self.assertThat(self.main_view.visible, Eventually(Equals(True)))

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
        category_page = self.app.wait_select_single(
            objectName='categorySelectionPage')
        self.main_view.get_header().click_action_button('deselectAllAction')
        list_item = category_page.wait_select_single(
            objectName='listItem', item_mod_id=category_id)
        self.pointing_device.click_object(list_item)
        continue_btn = category_page.wait_select_single(
            objectName='continueButton', visible=True)
        self.pointing_device.click_object(continue_btn)
        test_selection_page = self.app.wait_select_single(
            objectName='testSelectionPage')
        self.main_view.get_header().click_action_button('deselectAllAction')
        for job_id in job_ids:
            list_item = test_selection_page.wait_select_single(
                objectName='listItem', item_mod_id=job_id)
            list_item.swipe_into_view()
            self.pointing_device.click_object(list_item)
        continue_btn = test_selection_page.wait_select_single(
            objectName='continueButton')
        self.pointing_device.click_object(continue_btn)

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

    def _launch_application_from_desktop(self):
        app_qml_source_location = self._get_app_qml_source_path()
        if os.path.exists(app_qml_source_location):
            self.app = self.launch_test_application(
                base.get_qmlscene_launch_command(),
                '-I' + _get_module_include_path(),
                app_qml_source_location,
                '--autopilot',
                app_type='qt',
                emulator_base=emulators.UbuntuUIToolkitEmulatorBase)
        else:
            raise NotImplementedError(
                "On desktop we can't install click packages yet, so we can "
                "only run from source.")

    def _get_app_qml_source_path(self):
        qml_file_name = '{0}.qml'.format(self.app_name)
        return os.path.join(self._get_path_to_app_source(), qml_file_name)

    def _get_path_to_app_source(self):
        return os.path.join(get_path_to_source_root(), self.app_name)

    def _launch_application_from_phablet(self):
        # On phablet, we only run the tests against the installed click
        # package.
        self.app = self.launch_click_package(self.pacakge_id, self.app_name)

    @property
    def main_view(self):
        return self.app.select_single(emulators.MainView)
