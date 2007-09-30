import os
import optparse, gettext
from gettext import gettext as _

from hwtest.application import ApplicationManager
from hwtest.constants import SHARE_DIR
from hwtest.excluder import Excluder


DIRECTION_NEXT = 1
DIRECTION_PREVIOUS = 0


class UserInterface(object):
    '''Abstract base class for encapsulating the workflow and common code for
       any user interface implementation (like GTK, Qt, or CLI).

       A concrete subclass must implement all the abstract ui_* methods.'''

    def __init__(self):
        self.gettext_domain = 'hwtest'
        self.application = None
        self.questions = None

        gettext.textdomain(self.gettext_domain)
        self.parse_argv()

    def run_questions(self):
        # Determine category
        category = self.ui_present_categories(_("Hardware Categories"),
            _("Please specify the type of hardware being tested:"))
        exclude_func = lambda question, category=category: \
                       category not in question.categories

        # Iterate over questions
        manager_questions = self.application.get_questions()
        questions = Excluder(manager_questions, exclude_func, exclude_func)

        direction = DIRECTION_NEXT
        while questions.has_next():
            if direction == DIRECTION_NEXT:
                question = questions.next()
            elif direction == DIRECTION_PREVIOUS:
                question = questions.prev()
            else:
                raise Exception, "invalid direction: %s" % direction
            direction = self.ui_present_question(question, questions.has_prev(), questions.has_next())

        # Exchange question answers
        error = None
        while True:
            secure_id = self.ui_present_exchange(error)
            self.application.report.secure_id = secure_id
            self.application.run()
            error = self.application.plugin_manager.get_error()
            if not error:
                break

    def run_argv(self):
        self.application = ApplicationManager().create(self.options)
        self.run_questions()

    def parse_argv(self):
        optparser = optparse.OptionParser('%prog [options]')
        optparser.add_option("-q", "--questions", metavar="FILE",
                          default=os.path.join(SHARE_DIR, "questions.txt"),
                          help="The file containing certification questions.")
        optparser.add_option("-d", "--data-path", metavar="PATH",
                          default="~/.hwtest",
                          help="The directory to store data files in.")
        optparser.add_option("-l", "--log", metavar="FILE",
                          help="The file to write the log to.")
        optparser.add_option("--log-level",
                          default="critical",
                          help="One of debug, info, warning, error or critical.")

        (self.options, self.args) = optparser.parse_args()

    def ui_present_categories(self, title, text):
        raise NotImplementedError, 'this function must be overridden by subclasses'

    def ui_present_question(self, question, has_prev, has_next):
        raise NotImplementedError, 'this function must be overridden by subclasses'

    def ui_present_exchange(self, error):
        raise NotImplementedError, 'this function must be overridden by subclasses'
