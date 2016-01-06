# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

from testtools.matchers import Equals
from autopilot.matchers import Eventually
from autopilot.input import Keyboard

import checkbox_touch


class TestCheckboxTouch(checkbox_touch.ClickAppTestCase):

    def skip_test(self, selectable_object_name=None):
        """Skip current test using header action.

        :param selectable_object_name:
             the objectName of component that has to be visible and selecable
             before the action is clicked.
        """
        if selectable_object_name is not None:
            self.app.wait_select_single(
                objectName=selectable_object_name, visible=True)
        self.main_view.get_header().click_action_button('skip')
        dialog = self.app.wait_select_single(objectName='dialog')
        yes_btn = dialog.select_single(objectName='yesButton')
        self.pointing_device.click_object(yes_btn)
        keyboard = Keyboard.create('X11')
        comment_text = self.app.select_single(objectName='commentText')
        with keyboard.focused_type(comment_text) as kb:
            kb.type("Skipped by autopilot!")
        done_btn = self.app.select_single(objectName='doneButton')
        self.pointing_device.click_object(done_btn)

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
        self.main_view.get_header().click_action_button('toggleSelectionAction')
        category_id = '2015.com.canonical.certification::normal'
        list_item = category_page.wait_select_single(
            objectName='listItem', item_mod_id=category_id)
        self.pointing_device.click_object(list_item)
        continue_btn = category_page.wait_select_single(
            objectName='continueButton')
        self.pointing_device.click_object(continue_btn)
        tests_selection_page = self.app.wait_select_single(
            objectName='testSelectionPage', visible=True)
        continue_btn = tests_selection_page.wait_select_single(
            objectName='continueButton')
        self.pointing_device.click_object(continue_btn)
        # TWO automatic jobs should pass by:
        # autopilot/automated-test-that-fails
        # autopilot/automated-test-that-passes
        # now it's time for three manual jobs - autopilot/manual-{1,2,3}
        next_steps = [
            ('manualIntroPage', 'continueButton'),
            ('testVerificationPage', 'passButton'),
            ('manualIntroPage', 'continueButton'),
            ('testVerificationPage', 'failButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.skip_test('manualIntroPage')
        # Now it's time for three UIV tests -
        #  autopilot/user-interact-verify-{1,2,3}
        next_steps = [
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'passButton'),
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'failButton')
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.skip_test('userInteractVerifyIntroPage')
        # Next come 3 user-verify tests - autopilot/user-verify-{1,2,3}
        next_steps = [
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'passButton'),
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'failButton')
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.skip_test('userInteractVerifyIntroPage')
        # Now the user-interact tests - autopilot/user-interact-{1,2,3}
        next_steps = [
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('userInteractSummary', 'continueButton'),
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('userInteractSummary', 'continueButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.skip_test('userInteractVerifyIntroPage')
        # Next is autopilot/print-and-verify
        next_steps = [
            ('userInteractVerifyIntroPage', 'startTestButton'),
            ('testVerificationPage', 'passButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        # Next is a shell job that takes >10s to complete -
        # autopilot/print-and-verify
        # We have to use long_wait because wait_select_single would time-out.
        self.long_wait_select_single(
            self.app, objectName='qmlNativePage', visible=True)
        # Now, qml-native job already started. autpopilot/qml-job
        next_steps = [
            ('qmlNativePage', 'continueButton'),
            ('qmlTestPage', 'passButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        # we should see results screen now
        results = {'passed': '11', 'failed': '5', 'skipped': '5'}
        self.check_results(results)


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
            objectName='headerLabel', visible=True)
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
            objectName='headerLabel', visible=True)
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


class CommandOutputTests(checkbox_touch.ClickAppTestCase):
    def test_output_visible_while_automated_test_is_running(self):
        self.start_and_select_tests(
            '2015.com.canonical.certification::normal', [
                '2015.com.canonical.certification::autopilot/print-and-sleep'])
        page = self.app.wait_select_single(
            objectName='automatedTestPage', visible=True)
        button = page.wait_select_single(
            objectName='showOutputButton', visible=True)
        self.pointing_device.click_object(button)
        output_page = self.app.wait_select_single(
            objectName='commandOutputPage', visible=True)
        text_area = output_page.wait_select_single(
            objectName='textArea', visible=True)
        self.assertThat(text_area.text, Eventually(Equals("foobar\n")))

    def test_output_visible_on_verification(self):
        self.start_and_select_tests(
            '2015.com.canonical.certification::normal',
            ['2015.com.canonical.certification::autopilot/print-and-verify'])
        intro_page = self.app.wait_select_single(
            objectName='userInteractVerifyIntroPage', visible=True)
        start_button = intro_page.wait_select_single(
            objectName='startTestButton', visible=True)
        self.pointing_device.click_object(start_button)
        verification_page = self.app.wait_select_single(
            objectName='testVerificationPage', visible=True)
        show_output_button = verification_page.wait_select_single(
            objectName='showOutputButton', visible=True)
        self.pointing_device.click_object(show_output_button)
        output_page = self.app.wait_select_single(
            objectName='commandOutputPage', visible=True)
        text_area = output_page.wait_select_single(
            objectName='textArea', visible=True)
        self.assertThat(text_area.text, Eventually(Equals("foobar\n")))


class RerunTests(checkbox_touch.ClickAppTestCase):
    def test_rerun_after_rerun(self):
        test_id = '2015.com.canonical.certification::autopilot/manual-2'
        self.start_and_select_tests(
            '2015.com.canonical.certification::normal', [test_id])
        next_steps = [
            ('manualIntroPage', 'continueButton'),
            ('testVerificationPage', 'failButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        results_page = self.app.wait_select_single(
            objectName='resultsPage', visible=True)
        self.main_view.get_header().click_action_button('rerunAction')
        # we now should see a re-run screen; let's select the only test
        rerun_page = self.app.wait_select_single(
            objectName='rerunSelectionPage', visible=True)
        list_item = rerun_page.wait_select_single(
            objectName='listItem', item_mod_id=test_id)
        self.pointing_device.click_object(list_item)
        continue_btn = rerun_page.wait_select_single(
            objectName='continueButton', visible=True)
        self.pointing_device.click_object(continue_btn)
        # run the same steps as before
        self.process_sequence_of_clicks_on_pages(next_steps)
        results_page = self.app.wait_select_single(
            objectName='resultsPage', visible=True)
        self.main_view.get_header().click_action_button('rerunAction')
        # we should see the re-run screen again
        rerun_page = self.app.wait_select_single(
            objectName='rerunSelectionPage', visible=True)
        continue_btn = rerun_page.wait_select_single(
            objectName='continueButton', visible=True)
        self.pointing_device.click_object(continue_btn)
        self.check_results({'passed': '1', 'failed': '1', 'skipped': '0'})

    def test_rerun_after_fail(self):
        test_id = '2015.com.canonical.certification::autopilot/manual-2'
        self.start_and_select_tests(
            '2015.com.canonical.certification::normal', [test_id])
        next_steps = [
            ('manualIntroPage', 'continueButton'),
            ('testVerificationPage', 'failButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        results_page = self.app.wait_select_single(
            objectName='resultsPage', visible=True)
        self.main_view.get_header().click_action_button('rerunAction')
        # we now should see a re-run screen; let's select the only test
        rerun_page = self.app.wait_select_single(
            objectName='rerunSelectionPage', visible=True)
        list_item = rerun_page.wait_select_single(
            objectName='listItem', item_mod_id=test_id)
        self.pointing_device.click_object(list_item)
        continue_btn = rerun_page.wait_select_single(
            objectName='continueButton', visible=True)
        self.pointing_device.click_object(continue_btn)
        next_steps = [
            ('manualIntroPage', 'continueButton'),
            ('testVerificationPage', 'passButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        # now set the outcome to 'pass'; we should be on results screen now
        self.check_results({'passed': '2', 'failed': '0', 'skipped': '0'})

    def test_no_rerun_after_pass(self):
        test_id = '2015.com.canonical.certification::autopilot/manual-1'
        self.start_and_select_tests(
            '2015.com.canonical.certification::normal', [test_id])
        next_steps = [
            ('manualIntroPage', 'continueButton'),
            ('testVerificationPage', 'passButton'),
        ]
        self.process_sequence_of_clicks_on_pages(next_steps)
        self.check_results({'passed': '2', 'failed': '0', 'skipped': '0'})
