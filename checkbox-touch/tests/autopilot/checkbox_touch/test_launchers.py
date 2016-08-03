import checkbox_touch

class FullAutoLauncherTests(checkbox_touch.ClickAppTestCase):

    launcher = 'full-auto'

    def test_full_auto(self):
        password_box = self.long_wait_select_single(
            self.app, objectName='passwordBox')
        ok_btn = self.app.wait_select_single(objectName='cancelButton')
        self.pointing_device.click_object(ok_btn)
        results = {'passed': '7', 'failed': '2', 'skipped': '13'}
        self.check_results(results)

class ForceTestLauncherTests(checkbox_touch.ClickAppTestCase):

    launcher = 'force-test-not-silent'

    def test_force_test_not_silent(self):
        self.skipResumeIfShown()
        welcome_page = self.long_wait_select_single(
            self.app, objectName='welcomePage', state='loaded')
        start_btn = welcome_page.wait_select_single(
            objectName='startTestButton')
        self.pointing_device.click_object(start_btn)
        results = {'passed': '1', 'failed': '0', 'skipped': '0'}
        self.check_results(results)

class PreselectedTPLauncherTests(checkbox_touch.ClickAppTestCase):

    launcher = 'preselected-tp'

    def test_preselected_tp(self):
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
                '2015.com.canonical.certification::autopilot-alt'),
            item_mod_selected=True)

class FilteredTPLauncherTests(checkbox_touch.ClickAppTestCase):

    launcher = 'filtered-tp'

    def test_filtered_tp(self):
        self.skipResumeIfShown()
        welcome_page = self.long_wait_select_single(
            self.app, objectName='welcomePage', state='loaded')
        start_btn = welcome_page.wait_select_single(
            objectName='startTestButton')
        self.pointing_device.click_object(start_btn)
        # if filtering worked, we should be on the category selection screen
        category_page = self.app.wait_select_single(
            objectName='categorySelectionPage', visible=True)
