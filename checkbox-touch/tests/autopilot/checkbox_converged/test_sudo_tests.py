import os
import stat
import sys
import tempfile
import textwrap

from autopilot import input, platform
from autopilot.input import Keyboard

import checkbox_converged


class SudoTestCheckboxConverged(checkbox_converged.ClickAppTestCase):
    """
    Tests requiring sudo password.

    This class mocks sudo command by providing an executable of that name in
    $PATH. This way the tests can run password dialogs in a controlled
    environment.

    The mock is set up when launching the app, this guarantees that overwriten
    $PATH gets propagated to the app.
    """

    def tearDown(self):
        if platform.model() == 'Desktop':
            self.tear_down_mock()
        super().tearDown()

    def _launch_application_from_desktop(self):
		# mock done in setUp would not affect the execution, this is why it has
		# to be here
        self.setup_mock()
        super()._launch_application_from_desktop()

    def setup_mock(self):
        self._original_path = os.environ['PATH']
        self._tmpdir = tempfile.TemporaryDirectory()
        tmp_path = self._tmpdir.name

        mock_template = textwrap.dedent("""
            #!/usr/bin/env python3
            import sys
            expected_password = '0000'
            given_password = sys.stdin.readlines()[0].strip('\\n')
            if given_password != expected_password:
                raise SystemExit(1)
        """).strip('\n')

        mock_file = os.path.join(tmp_path, 'sudo')
        with open(mock_file, 'wt') as f:
            f.write(mock_template)
        st = os.stat(mock_file)
        os.chmod(mock_file, st.st_mode | stat.S_IEXEC)
        os.environ['PATH'] = tmp_path + os.pathsep + self._original_path

    def tear_down_mock(self):
        os.environ['PATH'] = self._original_path

    def test_smoke(self):
        test_id = '2015.com.canonical.certification::autopilot/sudo-right'
        self.start_and_select_tests(
            '2015.com.canonical.certification::sudo', [test_id])
        keyboard = Keyboard.create()
        password_box = self.app.wait_select_single(objectName='passwordBox')
        with keyboard.focused_type(password_box) as kb:
            kb.type("0000")
        ok_btn = self.app.wait_select_single(objectName='okButton')
        self.pointing_device.click_object(ok_btn)
        results = {'passed': '2', 'failed': '0', 'skipped': '0'}
        self.check_results(results)

    def test_wrong_password(self):
        test_id = '2015.com.canonical.certification::autopilot/sudo-right'
        self.start_and_select_tests(
            '2015.com.canonical.certification::sudo', [test_id])
        keyboard = Keyboard.create()
        password_box = self.app.wait_select_single(objectName='passwordBox')
        with keyboard.focused_type(password_box) as kb:
            kb.type("wrong")
        ok_btn = self.app.wait_select_single(objectName='okButton')
        self.pointing_device.click_object(ok_btn)
        results = {'passed': '1', 'failed': '1', 'skipped': '0'}
        self.check_results(results)

    def test_password_cancelled(self):
        test_id = '2015.com.canonical.certification::autopilot/sudo-right'
        self.start_and_select_tests(
            '2015.com.canonical.certification::sudo', [test_id])
        cancel_btn = self.app.wait_select_single(objectName='cancelButton')
        self.pointing_device.click_object(cancel_btn)
        results = {'passed': '1', 'failed': '0', 'skipped': '1'}
        self.check_results(results)
