# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

from testtools.matchers import Equals

import checkbox_touch


class LatchButtonTestCase(checkbox_touch.ClickAppTestCase):
    """Tests for the LatchButton component"""
    def test_latching(self):
        latch_button = self.app.select_single(objectName="latchButton")
        latch_button.swipe_into_view()
        signal = latch_button.watch_signal("latchedClicked()")
        self.pointing_device.click_object(latch_button)
        self.pointing_device.click_object(latch_button)  # click again!
        self.assertThat(signal.num_emissions, Equals(1))
