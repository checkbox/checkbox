# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

from testtools.matchers import Equals

import checkbox_touch


class ManualIntroPageTestCase(checkbox_touch.ClickAppTestCase):
    """Tests for the Intro page to Manual test"""

    def setUp(self):
        super(ManualIntroPageTestCase, self).setUp()
        # open ManualIntroPage by clicking on 'Manual test page' butotn
        button = self.main_view.select_single(
            objectName='manualIntroPageButton')
        self.pointing_device.click_object(button)
        self.page = self.app.select_single(objectName='manualIntroPage')

    def test_default_content(self):
        self.assertThat(self.page.title, Equals('Test Description'))

    def test_continue_button(self):
        continue_button = self.page.select_single(objectName='continueButton')
        self.assertThat(continue_button.text, Equals('Continue'))
        signal = self.page.watch_signal('continueClicked()')
        self.pointing_device.click_object(continue_button)
        self.assertThat(signal.was_emitted, Equals(True))

    def test_goes_to_verification(self):
        continue_button = self.page.select_single(objectName='continueButton')
        self.pointing_device.click_object(continue_button)
        next_page = self.app.select_single(objectName='testVerificationPage')
        self.assertThat(next_page.title, Equals('Verification'))
        page_stack = self.main_view.select_single(objectName='pageStack')
        self.assertThat(page_stack.depth, Equals(3))
