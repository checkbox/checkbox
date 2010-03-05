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

from checkbox.job import Job
from checkbox.user_interface import (UserInterface, ANSWER_TO_STATUS,
    ALL_ANSWERS, YES_ANSWER, NO_ANSWER, SKIP_ANSWER)


ANSWER_TO_OPTION = {
    YES_ANSWER: _("yes"),
    NO_ANSWER: _("no"),
    SKIP_ANSWER: _("skip")}

OPTION_TO_ANSWER = dict((o, a) for a, o in ANSWER_TO_OPTION.items())


class CLIDialog(object):
    """Command line dialog wrapper."""

    def __init__(self, text):
        self.text = text
        self.visible = False

    def put(self, text):
        sys.stdout.write(text)

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
        attributes[3] = attributes[3] & ~(termios.ICANON | termios.ECHO)
        attributes[6][termios.VMIN] = 1
        attributes[6][termios.VTIME] = 0
        termios.tcsetattr(fileno, termios.TCSANOW, attributes)

        input = []
        escape = 0
        try:
            while len(input) < limit:
                ch = str(sys.stdin.read(1))
                if ord(ch) == separator:
                    break
                elif ord(ch) == 033: # ESC
                    escape = 1
                elif ord(ch) == termios.CERASE or ord(ch) == 010:
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

                response = self.get(_("Please choose (%s): ") % ("/".join(self.keys)))
                if response >= 0:
                    return response

                if label is not None:
                    self.put_line(label)

        except KeyboardInterrupt:
            self.put_newline()
            raise

    def add_option(self, option, key=None):
        if key is None:
            key = string.lowercase[len(self.keys)]
        self.keys.append(key)
        self.options.append(option)


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


class CLIProgressDialog(CLIDialog):
    """Command line progress dialog wrapper."""

    def __init__(self, text):
        super(CLIProgressDialog, self).__init__(text)
        self.progress_count = 0

    def set(self, progress=None):
        self.progress_count = (self.progress_count + 1) % 5
        if self.progress_count:
            return

        if progress != None:
            self.put("\r%u%%" % (progress * 100))
        else:
            self.put(".")
        sys.stdout.flush()


class CLIInterface(UserInterface):

    def _toggle_results(self, key, options, results):
        if isinstance(results, dict):
            if key in results:
                del results[key]

            elif key in options:
                if isinstance(options[key], dict):
                    results[key] = {}
                elif isinstance(options[key], (list, tuple,)):
                    results[key] = []
                else:
                    raise Exception, "Unknown result type: %s" % type(results)

                for k in options[key]:
                    self._toggle_results(k, options[key], results[key])

        elif isinstance(results, (list, tuple,)):
            if key in results:
                results.remove(key)
            elif key in options:
                results.append(key)

        else:
            raise Exception, "Unknown result type: %s" % type(results)

    def show_progress_start(self, text):
        self.progress = CLIProgressDialog(text)
        self.progress.show()

    def show_progress_pulse(self):
        self.progress.set()

    def show_text(self, text, previous=None, next=None):
        dialog = CLIChoiceDialog(text)
        dialog.run()

    def show_entry(self, text, value, previous=None, next=None):
        dialog = CLILineDialog(text)

        return dialog.run()

    def show_check(self, text, options=[], default=[]):
        dialog = CLIChoiceDialog(text)
        for option in options:
            dialog.add_option(option)

        dialog.add_option("Space when finished", " ")

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

    def show_tree(self, text, options={}, default={}):
        keys = sorted(options.keys())
        values = [options[k] for k in keys]

        dialog = CLIChoiceDialog(text)
        for option in keys:
            dialog.add_option(option)

        dialog.add_option("Plus to expand options", "+")
        dialog.add_option("Space when finished", " ")

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
                branch_results =  results.get(result, {})
                self.show_tree(result, options[result], branch_results)
                if branch_results and result not in results:
                    results[result] = branch_results

        return results

    def _run_test(self, test):
        message = _("Running test %s...") % test["name"]
        # TODO: fix this to support running tests as root
        job = Job(test["command"], test.get("environ"),
            test.get("timeout"))
        (status, data, duration) = self.show_progress(message, job.execute)
        return data

    def show_test(self, test):
        options = list([ANSWER_TO_OPTION[a] for a in ALL_ANSWERS])
        if "command" in test:
            options.append(_("test"))

        if re.search(r"\$output", test["description"]):
            output = self._run_test(test)
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

            output = self._run_test(test)

            options[-1] = _("test again")

        answer = OPTION_TO_ANSWER[option]
        if answer == NO_ANSWER:
            text = _("Further information:")
            dialog = CLITextDialog(test.name, text)
            test["data"] = dialog.run(_("Please type here and press"
                " Ctrl-D when finished:\n"))
        else:
            test["data"] = ""

        test["status"] = ANSWER_TO_STATUS[answer]

    def show_info(self, text, options=[], default=None):
        return self.show_radio(text, options, default)

    def show_error(self, text):
        dialog = CLIChoiceDialog("Error: %s" % text)
        dialog.run()
