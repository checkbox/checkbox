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
