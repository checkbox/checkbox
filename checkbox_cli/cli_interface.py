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
import termios

from gettext import gettext as _

from checkbox.test import ALL_STATUS, FAIL, TestResult
from checkbox.user_interface import UserInterface


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
                for index, option in enumerate(self.options):
                    self.put_line("  %s: %s" % (self.keys[index], option))

                response = self.get(_("Please choose (%s): ") % ("/".join(self.keys)))
                try:
                    return self.keys.index(response[0].upper()) + 1
                except ValueError:
                    pass
        except KeyboardInterrupt:
            self.put_newline()
            raise

    def add_option(self, option):
        if "&" in option:
            key = re.search("&(.)", option, re.S).group(1).upper()
            option = re.sub("&", "", option)
        else:
            key = " "

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

    def show_wait(self, text, function, *args, **kwargs):
        self.progress = CLIProgressDialog(text)
        self.progress.show()
        self.do_function(function, *args, **kwargs)

    def show_pulse(self):
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
            label = "&%s" % option.capitalize()
            dialog.add_option(label)

        dialog.add_option("& Space when finished")

        results = {}
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
            label = "&%s" % option.capitalize()
            dialog.add_option(label)

        # Show options dialog
        response = dialog.run()
        return options[response - 1]

    def show_test(self, test, result=None):
        answers = [_("yes"), _("no"), _("skip")]
        if str(test.command):
            answers.append(_("test"))

        while True:
            # Show answer dialog
            description = test.description(result)
            dialog = CLIChoiceDialog(description)

            for answer in answers:
                dialog.add_option("&%s" % answer)

            # Get answer from dialog
            response = dialog.run()
            answer = answers[response - 1]
            if response <= len(ALL_STATUS):
                break

            self.progress = CLIProgressDialog(
                _("Running test %s...") % test.name)
            self.progress.show()

            result = self.do_function(test.command)
            answers[-1] = _("test again")

        status = dict(zip(answers[0:len(ALL_STATUS)], ALL_STATUS))[answer]
        if status == FAIL:
            text = _("Further information:")
            dialog = CLITextDialog(test.name, text)
            data = dialog.run(_("Please type here and press"
                " Ctrl-D when finished:\n"))
        else:
            data = ""

        return TestResult(test, status, data)

    def show_error(self, text):
        dialog = CLIChoiceDialog("Error: %s" % text)
        dialog.run()
