#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import re
import sys
import string
import termios

from gettext import gettext as _

from checkbox.user_interface import (UserInterface, ANSWER_TO_STATUS,
    ALL_ANSWERS, YES_ANSWER, NO_ANSWER, SKIP_ANSWER)


ANSWER_TO_OPTION = {
    YES_ANSWER: _("yes"),
    NO_ANSWER: _("no"),
    SKIP_ANSWER: _("skip")}

OPTION_TO_ANSWER = dict((o, a) for a, o in ANSWER_TO_OPTION.items())


class CLIDialog:
    """Command line dialog wrapper."""

    def __init__(self, text):
        self.text = text
        self.visible = False

    def put(self, text):
        sys.stdout.write(text)
        sys.stdout.flush()

    def put_line(self, line):
        self.put("%s\n" % line)

    def put_newline(self):
        self.put("\n")

    def get(self, label=None, limit=1, separator=termios.CEOT):
        if label is not None:
            self.put_newline()
            self.put(label)

        fileno = sys.stdin.fileno()
        saved_attributes = termios.tcgetattr(fileno)
        attributes = termios.tcgetattr(fileno)
        attributes[3] &= ~(termios.ICANON | termios.ECHO)
        attributes[6][termios.VMIN] = 1
        attributes[6][termios.VTIME] = 0
        termios.tcsetattr(fileno, termios.TCSANOW, attributes)

        input = []
        escape = 0
        try:
            while len(input) < limit:
                ch = sys.stdin.read(1)
                if ord(ch) == separator:
                    break
                elif ord(ch) == 0o33:  # ESC
                    escape = 1
                elif ord(ch) == termios.CERASE or ord(ch) == 0o10:
                    if len(input):
                        self.put("\010 \010")
                        del input[-1]
                elif ord(ch) == termios.CKILL:
                    self.put("\010 \010" * len(input))
                    input = []
                else:
                    if not escape:
                        input.append(ch)
                        self.put(ch)
                    elif escape == 1:
                        if ch == "[":
                            escape = 2
                        else:
                            escape = 0
                    elif escape == 2:
                        escape = 0
        finally:
            termios.tcsetattr(fileno, termios.TCSANOW, saved_attributes)

        return "".join(input)

    def show(self):
        self.visible = True
        self.put_newline()
        self.put_line(self.text)


class CLIChoiceDialog(CLIDialog):

    def __init__(self, text):
        super(CLIChoiceDialog, self).__init__(text)
        self.keys = []
        self.options = []

    def get(self, *args, **kwargs):
        response = super(CLIChoiceDialog, self).get(*args, **kwargs)
        try:
            return self.keys.index(response[0])
        except ValueError:
            return -1

    def run(self, label=None, defaults=[]):
        if not self.visible:
            self.show()

        try:
            # Only one option
            if len(self.keys) <= 1:
                self.get(_("Press any key to continue..."))
                return 0
            # Multiple choices
            while True:
                self.put_newline()
                for key, option in zip(self.keys, self.options):
                    default = "*" if option in defaults else " "
                    self.put_line("%s %s: %s" % (default, key, option))

                response = self.get(_("Please choose (%s): ") %
                                     ("/".join(self.keys)))
                if response >= 0:
                    return response

                if label is not None:
                    self.put_line(label)

        except KeyboardInterrupt:
            self.put_newline()
            raise

    def add_option(self, option, key=None):
        if key is None:
            keys = option.lower() + \
                   string.ascii_letters + \
                   string.digits + \
                   string.punctuation

            keys = keys.replace(' ', '')
            keys = keys.replace('+', '')

            for key in keys:
                if key not in self.keys:
                    break
        self.keys.append(key)
        self.options.append(option)


class CLIReportDialog(CLIDialog):
    """
    Display test results
    """
    STATUS = {'pass': '[0;32m{0}[0m',
              'fail': '[0;31m{0}[0m'}

    def __init__(self, text, results):
        super(CLIReportDialog, self).__init__(text)
        self.results = results

    def run(self):
        """
        Show root of the tree
        and provide the ability to further display subtress
        """
        root = self.results
        title = self.text
        self._display(title, root)

    def _is_suite(self, root):
        """
        Return True if root contains a suite
        that is, a job containing other jobs
        """
        return all(issubclass(type(value), dict)
                   for value in root.values())

    def _display(self, title, root):
        """
        Display dialog until user decides to exit
        (recursively for subtrees)
        """
        while True:
            self.put_newline()
            self.put_newline()
            self.put_line(title)
            self.put_newline()

            keys = []
            options = []

            def add_option(option, key=None):
                """
                Add option to list
                and generate automatic key value
                if not provided
                """
                if key is None:
                    key = string.ascii_lowercase[len(keys)]
                keys.append(key)
                options.append(option)

            for job_name, job_data in sorted(root.items()):
                if self._is_suite(job_data):
                    add_option(job_name)
                    self.put_line('{key}: {option}'
                                  .format(key=keys[-1],
                                          option=options[-1]))
                else:
                    job_status = job_data.get('status')
                    status_string = (self.STATUS.get(job_status, '{0}')
                                     .format(job_status))
                    self.put_line('   {name} [{status}]'
                                  .format(name=job_name,
                                          status=status_string))

            add_option(_("Space when finished"), " ")
            self.put_line('{key}: {option}'
                          .format(key=keys[-1],
                                  option=options[-1]))

            response = self.get(_("Please choose (%s): ") % ("/".join(keys)))

            if response != ' ':
                try:
                    selected_option = options[keys.index(response)]
                except ValueError:
                    # Display again menu
                    continue

                # Display new menu with the contents of the selected option
                self._display(selected_option, root[selected_option])
            else:
                # Exit from this menu display
                # (display again parent menu or exit)
                break


class CLITextDialog(CLIDialog):

    limit = 255
    separator = termios.CEOT

    def run(self, label=None):
        if not self.visible:
            self.show()

        self.put_newline()
        try:
            return self.get(label, self.limit, self.separator)
        except KeyboardInterrupt:
            self.put_newline()
            raise


class CLILineDialog(CLITextDialog):

    limit = 80
    separator = ord("\n")


class Twirly(object):
    def __init__(self):
        self.index = 0
        self.twirlies = "-\\|/"

    def next(self):
        next_twirly = self.twirlies[self.index]
        self.index = (self.index + 1) % len(self.twirlies)
        return next_twirly


class CLIProgressDialog(CLIDialog):
    """Command line progress dialog wrapper."""

    def __init__(self, text):
        super(CLIProgressDialog, self).__init__(text)
        self.progress_count = 0
        self.twirly = Twirly()

    def set(self, progress=None):
        self.progress_count = (self.progress_count + 1) % 5
        if self.progress_count:
            return

        if progress != None:
            self.put("\r%u%%" % (progress * 100))
        else:
            self.put("\b\b")
            self.put(self.twirly.next())
            self.put(" ")
        sys.stdout.flush()


class CLIInterface(UserInterface):

    def _toggle_results(self, key, options, results):
        if isinstance(results, dict):
            if key in results:
                del results[key]

            elif key in options:
                if isinstance(options[key], dict):
                    results[key] = {}
                elif isinstance(options[key], (list, tuple)):
                    results[key] = []
                else:
                    results[key] = None

                for k in options[key]:
                    self._toggle_results(k, options[key], results[key])

        elif isinstance(results, (list, tuple)):
            if key in results:
                results.remove(key)
            elif key in options:
                results.append(key)

    def show_progress_start(self, text):
        self.progress = CLIProgressDialog(text)
        self.progress.show()

    def show_progress_pulse(self):
        self.progress.set()

    def show_text(self, text, previous=None, next=None):
        dialog = CLIChoiceDialog(text)
        dialog.run()

    def show_entry(self, text, value, label=None, previous=None, next=None):
        dialog = CLILineDialog(text)

        return dialog.run()

    def show_check(self, text, options=[], default=[]):
        dialog = CLIChoiceDialog(text)
        for option in options:
            dialog.add_option(option)

        dialog.add_option(_("Space when finished"), " ")

        results = default
        while True:
            response = dialog.run(defaults=results)
            if response >= len(options):
                break

            result = options[response]
            self._toggle_results(result, options, results)

        return results

    def show_radio(self, text, options=[], default=None):
        dialog = CLIChoiceDialog(text)
        for option in options:
            dialog.add_option(option)

        # Show options dialog
        response = dialog.run()
        return options[response]

    def show_tree(self, text, options={}, default={}, deselect_warning=""):
        keys = sorted(options.keys())

        dialog = CLIChoiceDialog(text)
        for option in keys:
            dialog.add_option(option)

        dialog.add_option(_("Combine with character above to expand node"),
                          "+")
        dialog.add_option(_("Space when finished"), " ")

        do_expand = False
        results = default
        while True:
            response = dialog.run(defaults=results)
            if response > len(options):
                break

            elif response == len(options):
                response = dialog.get()
                do_expand = True

            else:
                do_expand = False

            # Invalid response
            if response < 0:
                continue

            # Toggle results
            result = keys[response]
            if not do_expand:
                self._toggle_results(result, options, results)
                continue

            # Expand tree
            dialog.visible = False
            if options[result]:
                branch_results = results.get(result, {})
                self.show_tree(result, options[result], branch_results)
                if branch_results and result not in results:
                    results[result] = branch_results

        return results

    def show_report(self, text, results):
        """
        Show test case results in a tree hierarchy
        """
        dialog = CLIReportDialog(text, results)
        dialog.run()

    def show_test(self, test, runner):
        options = list([ANSWER_TO_OPTION[a] for a in ALL_ANSWERS])
        if "command" in test:
            options.append(_("test"))

        if re.search(r"\$output", test["description"]):
            output = runner(test)[1]
        else:
            output = ""

        while True:
            # Show option dialog
            description = string.Template(test["description"]).substitute({
                "output": output.strip()})
            dialog = CLIChoiceDialog(description)

            for option in options:
                dialog.add_option(option, option[0])

            # Get option from dialog
            response = dialog.run()
            option = options[response]
            if response < len(ALL_ANSWERS):
                break

            output = runner(test)[1]

            options[-1] = _("test again")

        answer = OPTION_TO_ANSWER[option]
        if answer == NO_ANSWER:
            text = _("Further information:")
            dialog = CLITextDialog(text)
            test["data"] = dialog.run(_("Please type here and press"
                " Ctrl-D when finished:\n"))
        else:
            test["data"] = ""

        test["status"] = ANSWER_TO_STATUS[answer]

    def show_info(self, text, options=[], default=None):
        return self.show_radio(text, options, default)

    def show_error(self, primary_text,
                   secondary_text=None, detailed_text=None):
        text = filter(None, [primary_text, secondary_text, detailed_text])
        text = '\n'.join(text)
        dialog = CLIChoiceDialog("Error: %s" % text)
        dialog.run()
