# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

from testtools.matchers import Equals
from autopilot.matchers import Eventually

import checkbox_touch


class TestCheckboxTouch(checkbox_touch.ClickAppTestCase):

    def skip_test(self):
        """Skip current test using header action."""
        self.main_view.get_header().click_action_button('skip')
        dialog = self.app.wait_select_single(objectName='dialog')
        yes_btn = dialog.select_single(objectName='yesButton')
        self.pointing_device.click_object(yes_btn)

    def process_sequence_of_clicks_on_pages(self, steps):
        """
        Do a sequence of clicks on simple page->component hierarchies.

        :param steps:
            sequence of (page-objectName, component-objectName) pairs to go
            through.

        Typical run of checkbox-touch requires user to go through a sequence of
        pages that have pass/fail buttons on them. This function helps go
        through a sequence like that.
        """
        for parent, component in steps:
            self.app.wait_select_single(
                objectName=parent, visible=True)
            clickable = self.main_view.wait_select_single(
                objectName=component, visible=True)
            self.pointing_device.click_object(clickable)

    def test_launches(self):
        main_view = self.app.select_single(objectName='mainView')
        self.assertThat(main_view.visible, Eventually(Equals(True)))

    def test_full_run(self):
        """
        Test whether typical, full run of checkbox-touch works.

        This test launches checkbox-touch and runs all tests present in the
        autopilot provider. Tests that let user decide the outcome are served
        in three instances; one that user is supposed to pass, one that
        user should skip and the one that user should fail.
        The tests that have outcome determined automatically should come
        in two flavours; one that passes and one that fails.
        """
        self.skipResumeIfShown()
        welcome_page = self.long_wait_select_single(
            self.app, objectName='welcomePage', state='loaded')
        start_btn = welcome_page.wait_select_single(
            objectName='startTestButton')
        self.pointing_device.click_object(start_btn)
        category_page = self.app.wait_select_single(
            objectName='categorySelectionPage', visible=True)
        continue_btn = category_page.wait_select_single(
            objectName='continueButton')
        self.pointing_device.click_object(continue_btn)
        tests_selection_page = self.app.wait_select_single(
            objectName='testSelectionPage', visible=True)
        continue_btn = tests_selection_page.wait_select_single(
            objectName='continueButton')
        self.pointing_device.click_object(continue_btn)
        next_steps = [
            ('manualIntroPage', 'continueButton'),
            ('testVerificationPage', 'passButton'),
            ('manualIntroPage', 'continueButton'),
            ('testVerificationPage', 'failButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.skip_test()
        next_steps = [
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'passButton'),
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'failButton')
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.skip_test()
        next_steps = [
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'passButton'),
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'failButton')
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.skip_test()
        next_steps = [
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('userInteractSummary', 'continueButton'),
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('userInteractSummary', 'continueButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.skip_test()
        # we should see results screen now
        results = {'passed': '5', 'failed': '5', 'skipped': '4'}
        results_page = self.app.wait_select_single(objectName='resultsPage')
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


class SessionResumeTests(checkbox_touch.ClickAppTestCase):
    def select_two_tests_and_quit(self):
        self.start_and_select_tests(
            '2015.com.canonical.certification::normal', [
                '2015.com.canonical.certification::autopilot/user-verify-1',
                '2015.com.canonical.certification::autopilot/user-verify-2'])
        # make sure that test is shown (therefore session has been started)
        self.app.wait_select_single(
            objectName='userInteractVerifyIntroPage', visible=True)
        self.app.process.terminate()

    def test_rerun_after_resume(self):
        self.select_two_tests_and_quit()
        self.launch_application()
        self.assertThat(self.main_view.visible, Eventually(Equals(True)))
        # not doing long-wait, as the app was recently launched and it
        # *shouldn't* take long to relaunch it
        resume_page = self.app.wait_select_single(
            objectName='resumeSessionPage', visible=True)
        rerun_btn = resume_page.wait_select_single(
            objectName='rerunButton', visible=True)
        self.pointing_device.click_object(rerun_btn)
        intro_page = self.app.wait_select_single(
            objectName='userInteractVerifyIntroPage', visible=True)
        test_name_label = intro_page.wait_select_single(
            objectName='testNameLabel', visible=True)
        self.assertThat(test_name_label.text,
                        Eventually(Equals('autopilot/user-verify-1')))

    def test_continue_after_resume(self):
        self.select_two_tests_and_quit()
        self.launch_application()
        self.assertThat(self.main_view.visible, Eventually(Equals(True)))
        resume_page = self.app.wait_select_single(
            objectName='resumeSessionPage', visible=True)
        continue_btn = resume_page.wait_select_single(
            objectName='continueButton')
        self.pointing_device.click_object(continue_btn)
        intro_page = self.app.wait_select_single(
            objectName='userInteractVerifyIntroPage', visible=True)
        test_name_label = intro_page.wait_select_single(
            objectName='testNameLabel', visible=True)
        self.assertThat(test_name_label.text,
                        Eventually(Equals('autopilot/user-verify-2')))

    def test_restart_after_resume(self):
        self.select_two_tests_and_quit()
        self.launch_application()
        self.assertThat(self.main_view.visible, Eventually(Equals(True)))
        resume_page = self.app.wait_select_single(
            objectName='resumeSessionPage', visible=True)
        restart_btn = resume_page.wait_select_single(
            objectName='restartButton')
        self.pointing_device.click_object(restart_btn)
        welcome_page = self.app.wait_select_single(
            objectName='welcomePage')
        self.assertThat(welcome_page.visible, Eventually(Equals(True)))
