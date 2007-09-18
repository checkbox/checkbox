import os
import logging

from logging import StreamHandler, FileHandler, Formatter
from optparse import OptionParser

from hwtest.contrib import bpickle_dbus
from hwtest.contrib.persist import Persist

from hwtest import VERSION

from hwtest.plugins import (DeviceInfo, DistributionInfo,
    PackageInfo, MessageExchange)
from hwtest.plugin import PluginManager

from hwtest.gui import Gui
from hwtest.message_store import MessageStore
from hwtest.question import parse_file
from hwtest.reactor import Reactor
from hwtest.test import Test, TestManager
from hwtest.transport import HTTPTransport
from hwtest.constants import SHARE_DIR


class Application(object):

    title = "Hardware Usability Tool"

    intro = "Please specify the type of hardware being tested:"
 
    def __init__(self, transport, reactor, questions, data_path,
                 log_handlers=None, log_level=None):

        # Logging setup
        format = ("%(asctime)s %(levelname)-8s %(message)s")
        if log_handlers:
            for handler in log_handlers:
                handler.setFormatter(Formatter(format))
                logging.getLogger().addHandler(handler)
            if log_level:
                logging.getLogger().setLevel(log_level)
        elif not logging.getLogger().handlers:
            logging.disable(logging.CRITICAL)

        # Reactor setup
        if reactor is None:
            reactor = Reactor()
        self.reactor = reactor

        # Persist setup
        persist_filename = os.path.join(data_path, "data.bpickle")
        self.persist = self.get_persist(persist_filename)

        # Message store setup
        directory = os.path.join(data_path, "messages")
        self.message_store = MessageStore(reactor, self.persist, directory)

        # Test manager setup
        self.test_manager = TestManager(self.message_store)

        # Questions
        questions = parse_file(questions)
        tests = [Test(**q) for q in questions]
        for test in tests:
            self.test_manager.add(test)

        # Plugin manager setup
        self.plugin_manager = PluginManager(self.reactor, self.message_store,
            self.persist, persist_filename)

        # Default plugins
        plugins = self.get_default_plugins()
        for plugin in plugins:
            self.plugin_manager.add(plugin)

        # Test plugins
        for test in tests:
            self.plugin_manager.add(test)

        # Required plugins
        self.plugin_manager.add(MessageExchange(transport))

    def get_persist(self, persist_filename):
        persist = Persist()

        if os.path.exists(persist_filename):
            persist.load(persist_filename)
        persist.save(persist_filename)
        return persist

    def get_default_plugins(self):
        return [DistributionInfo(),
                DeviceInfo(),
                PackageInfo()]

    def run(self):
        try:
            bpickle_dbus.install()
            self.reactor.run()
            bpickle_dbus.uninstall()
        except:
            logging.exception("Error running reactor.")
            bpickle_dbus.uninstall()
            raise

        self.message_store.delete()


def make_parser():
    parser = OptionParser(version=VERSION)
    parser.add_option("-q", "--questions", metavar="FILE",
                      default=os.path.join(SHARE_DIR, "questions.txt"),
                      help="The file containing certification questions.")
    parser.add_option("-u", "--url",
                      default="https://certification.canonical.com/message",
                      help="The server URL to connect to.")
    parser.add_option("-d", "--data-path", metavar="PATH",
                      default="~/.hwtest",
                      help="The directory to store data files in.")
    parser.add_option("-l", "--log", metavar="FILE",
                      help="The file to write the log to.")
    parser.add_option("--log-level",
                      default="critical",
                      help="One of debug, info, warning, error or critical.")
    parser.add_option("-c", "--command-line",
                      default=False,
                      help="Run the tool from the command line.")
    return parser
 
def make_application(options):
    log_level = logging.getLevelName(options.log_level.upper())
    log_handlers = []
    log_handlers.append(StreamHandler())
    if options.log:
        log_filename = options.log
        log_handlers.append(FileHandler(log_filename))

    transport = HTTPTransport(options.url)
    reactor = Reactor()

    data_path = os.path.expanduser(options.data_path)

    return Application(transport, reactor,
        questions=options.questions, data_path=data_path,
        log_handlers=log_handlers, log_level=log_level)

def run(args):
    """Parse command line options, construct an application, and run it."""
    parser = make_parser()
    options = parser.parse_args(args)[0]
    application = make_application(options)

    ui = Gui(application)
    ui.main()
    return 0
