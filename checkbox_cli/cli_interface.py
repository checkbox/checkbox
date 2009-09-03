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

        self.put_newline()
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

    def run(self, label=None):
        if not self.visible:
            self.show()

        self.put_newline()
        try:
            # Only one option
            if len (self.keys) <= 1:
                self.get(_("Press any key to continue..."))
                return 0
            # Multiple choices
            while True:
                if label is not None:
                    self.put_line(label)
                for key, option in zip(self.keys, self.options):
                    self.put_line("  %s: %s" % (key, option))

                response = self.get(_("Please choose (%s): ") % ("/".join(self.keys)))
                try:
                    return self.keys.index(response[0].upper()) + 1
                except ValueError:
                    pass
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
            response = self.get(label, self.limit, self.separator)
            return response
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
            dialog.add_option(option.capitalize())

        dialog.add_option("Space when finished", " ")

        results = dict((d, True) for d in default)
        while True:
            response = dialog.run()
            if response > len(options):
                break

            result = options[response - 1]
            results[result] = True

        return results.keys()

    def show_radio(self, text, options=[], default=None):
        dialog = CLIChoiceDialog(text)
        for option in options:
            dialog.add_option(option.capitalize())

        # Show options dialog
        response = dialog.run()
        return options[response - 1]

    def _run_test(self, test):
        message = _("Running test %s...") % test["name"]
        job = Job(test["command"], test.get("environ"), test.get("timeout"))
        self.show_progress(message, job.execute)

    def show_test(self, test):
        options = list([ANSWER_TO_OPTION[a] for a in ALL_ANSWERS])
        if "command" in test:
            options.append(_("test"))

        if re.search(r"\$output", test["description"]):
            self._run_test(test)

        while True:
            # Show option dialog
            description = string.Template(test["description"]).substitute({
                "output": test.get("data", "").strip()})
            dialog = CLIChoiceDialog(description)

            for option in options:
                dialog.add_option(option.capitalize())

            # Get option from dialog
            response = dialog.run()
            option = options[response - 1]
            if response <= len(ALL_ANSWERS):
                break

            self._run_test(test)

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
