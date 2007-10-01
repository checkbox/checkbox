import sys, re
import termios

from hwtest.user_interface import UserInterfacePlugin


try:
    from gettext import gettext as _
    from hwtest.user_interface import UserInterface
except ImportError, e:
    # this can happen while upgrading python packages
    print >> sys.stderr, 'Could not import module, is a package upgrade in progress? Error: ', e
    sys.exit(1)


class CLIDialog(object):
    '''Command line dialog wrapper.'''

    def __init__(self, heading, text):
        self.heading = '\n*** ' + heading + '\n'
        self.text = text
        self.keys = []
        self.buttons = []
        self.visible = False

    def raw_input_char(self, text):
        """ raw_input, but read only one character """

        sys.stdout.write(text + ' ')

        file = sys.stdin.fileno()
        saved_attributes = termios.tcgetattr(file)
        attributes = termios.tcgetattr(file)
        attributes[3] = attributes[3] & ~(termios.ICANON)
        attributes[6][termios.VMIN] = 1
        attributes[6][termios.VTIME] = 0
        termios.tcsetattr(file, termios.TCSANOW, attributes)

        try:
            ch = str(sys.stdin.read(1))
        finally:
            termios.tcsetattr(file, termios.TCSANOW, saved_attributes)

        print
        return ch

    def show(self):
        self.visible = True
        print self.heading
        print self.text

    def run(self):
        if not self.visible:
            self.show()

        print
        try:
            # Only one button
            if len (self.keys) <= 1:
                self.raw_input_char(_('Press any key to continue...'))
                return 0
            # Multiple choices
            while True:
                print _('What would you like to do? Your options are:')
                for index, button in enumerate(self.buttons):
                    print '  %s: %s' % (self.keys[index], button)

                response = self.raw_input_char(_('Please choose (%s):') % ('/'.join(self.keys)))
                try:
                    return self.keys.index(response[0].upper()) + 1
                except ValueError:
                    pass
        except KeyboardInterrupt:
            print
            sys.exit(1)

    def addbutton(self, button):
        self.keys.append(re.search('&(.)', button).group(1).upper())
        self.buttons.append(re.sub('&', '', button))
        return len(self.keys)
 

class CLIInterface(UserInterface):

    def show_categories(self, title, text):
        dialog = CLIDialog(title, text)
        categories = ['desktop', 'laptop', 'server']
        for category in categories:
            report = dialog.addbutton('&%s' % category)

        # show categories dialog
        response = dialog.run()
        return categories[response - 1]

    def show_question(self, question, has_prev=False, has_next=False):
        dialog = CLIDialog(question.name, question.description)
        answers = ['yes', 'no', 'skip']
        for answer in answers:
            report = dialog.addbutton('&%s' % answer)

        # show answers dialog
        response = dialog.run()
        if answers[response - 1] is 'no':
            # prompt for comment
            pass

        return 1

    def show_exchange(self, error=None):
        # TODO: prompt for email
        pass


class CLIInterfacePlugin(UserInterfacePlugin):
    def __init__(self):
        super(CLIInterfacePlugin, self).__init__(CLIInterface())


factory = CLIInterfacePlugin
