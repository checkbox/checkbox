import re
import sys
import termios

from gettext import gettext as _
from hwtest.user_interface import UserInterface


class CLIDialog(object):
    """Command line dialog wrapper."""

    def __init__(self, heading, text):
        self.heading = heading
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
        attributes[3] = attributes[3] & ~(termios.ICANON)
        attributes[6][termios.VMIN] = 1
        attributes[6][termios.VTIME] = 0
        termios.tcsetattr(fileno, termios.TCSANOW, attributes)

        input = ""
        try:
            while len(input) < limit:
                ch = str(sys.stdin.read(1))
                if ord(ch) == separator:
                    break
                input += ch
        finally:
            termios.tcsetattr(fileno, termios.TCSANOW, saved_attributes)

        self.put_newline()
        return input

    def show(self):
        self.visible = True
        self.put_newline()
        self.put_line("*** %s" % self.heading)
        self.put_newline()
        self.put_line(self.text)


class CLIChoiceDialog(CLIDialog):

    def __init__(self, heading, text):
        super(CLIChoiceDialog, self).__init__(heading, text)
        self.keys = []
        self.buttons = []

    def run(self, label=None):
        if not self.visible:
            self.show()

        self.put_newline()
        try:
            # Only one button
            if len (self.keys) <= 1:
                self.get(_("Press any key to continue..."))
                return 0
            # Multiple choices
            while True:
                if label is not None:
                    self.put_line(label)
                for index, button in enumerate(self.buttons):
                    self.put_line("  %s: %s" % (self.keys[index], button))

                response = self.get(_("Please choose (%s): ") % ("/".join(self.keys)))
                try:
                    return self.keys.index(response[0].upper()) + 1
                except ValueError:
                    pass
        except KeyboardInterrupt:
            self.put_newline()
            sys.exit(1)

    def add_button(self, button):
        self.keys.append(re.search("&(.)", button).group(1).upper())
        self.buttons.append(re.sub("&", "", button))
        return len(self.keys)
 

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
            sys.exit(1)


class CLILineDialog(CLITextDialog):

    limit = 80
    separator = ord("\n")


class CLIProgressDialog(CLIDialog):
    """Command line progress dialog wrapper."""

    def __init__(self, heading, text):
        super(CLIProgressDialog, self).__init__(heading, text)
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

    def show_wait(self, message):
        title = "Hardware Test"
        self.progress = CLIProgressDialog(title, message)
        self.progress.show()

    def show_pulse(self):
        self.progress.set()

    def show_category(self):
        title = "Hardware Test"
        text = "Please select the category of your hardware."
        dialog = CLIChoiceDialog(title, text)
        categories = ["desktop", "laptop", "server"]
        for category in categories:
            dialog.add_button("&%s" % category)

        # show categories dialog
        response = dialog.run()
        return categories[response - 1]

    def show_question(self, question, has_prev=False, has_next=False):
        question.run()
        dialog = CLIChoiceDialog(question.name, question.description)
        answers = ["yes", "no", "skip"]
        for answer in answers:
            dialog.add_button("&%s" % answer)

        # show answers dialog
        response = dialog.run()
        status = answers[response - 1]
        data = ""
        if status is "no":
            text = "Please provide comments about the failure."
            dialog = CLITextDialog(question.name, text)
            data = dialog.run("Please type here and press"
                " Ctrl-D when finished:\n")

        question.set_answer(status, data)

        return 1

    def show_exchange(self, message=None, error=None):
        title = "Authentication"
        text = message or "Please provide your Launchpad email address:"
        dialog = CLILineDialog(title, text)

        if error:
            dialog.put("ERROR: %s" % error)

        email = dialog.run()
        return email

    def show_final(self, message=None):
        title = "Done"
        text = "Successfully sent information to server!"
        dialog = CLIChoiceDialog(title, text)

        return dialog.run()

    def show_error_message(self, title, text):
        dialog = CLIDialog("Error: %s" % title, text)
        dialog.addbutton("&Confirm")
        dialog.run()
