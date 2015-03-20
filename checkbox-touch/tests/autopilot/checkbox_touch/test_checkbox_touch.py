# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-

from testtools.matchers import Equals
from autopilot.matchers import Eventually

import checkbox_touch

class TestCheckboxTouch(checkbox_touch.ClickAppTestCase):
    """Test checking if app launches"""
    def test_launches(self):
        main_view = self.app.select_single(objectName='mainView')
        self.assertThat(main_view.visible, Eventually(Equals(True)))
