# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

"""Tests for the Hello World"""

from testtools.matchers import Equals

import checkbox_touch


class ResumeSessionScreenTestCase(checkbox_touch.ClickAppTestCase):
    """Tests for resume session screen"""

    def setUp(self):
        super(ResumeSessionScreenTestCase, self).setUp()
        # click "resume session page"
        button = self.main_view.select_single(
            objectName='resumeSessionPageButton')
        self.pointing_device.click_object(button)
        self.page = self.app.select_single(objectName='resumeSessionPage')

    def test_default_content(self):
        self.assertThat(self.page.title, Equals('Resume session'))
        button_texts = [('rerunButtonLabel', 'Rerun last'),
                        ('continueButtonLabel', 'Continue'),
                        ('restartButtonLabel', 'Restart')]
        for obj_name, text in button_texts:
            obj = self.main_view.select_single(objectName=obj_name)
            self.assertThat(obj.text, Equals(text))

    def test_signal_rerun_last(self):
        signal_watcher = self.page.watch_signal('rerunLast()')
        button = self.main_view.select_single(objectName='rerunButton')
        self.pointing_device.click_object(button)
        self.assertThat(signal_watcher.was_emitted, Equals(True))
        page_stack = self.main_view.select_single(objectName='pageStack')
        self.assertThat(page_stack.depth, Equals(1))

    def test_signal_continue_session(self):
        signal_watcher = self.page.watch_signal('continueSession()')
        button = self.main_view.select_single(objectName='continueButton')
        self.pointing_device.click_object(button)
        self.assertThat(signal_watcher.was_emitted, Equals(True))
        page_stack = self.main_view.select_single(objectName='pageStack')
        self.assertThat(page_stack.depth, Equals(1))

    def test_signal_restart_session(self):
        signal_watcher = self.page.watch_signal('restartSession()')
        button = self.main_view.select_single(objectName='restartButton')
        self.pointing_device.click_object(button)
        self.assertThat(signal_watcher.was_emitted, Equals(True))
        page_stack = self.main_view.select_single(objectName='pageStack')
        self.assertThat(page_stack.depth, Equals(1))
