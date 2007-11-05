import os
import sys
import logging

from logging import StreamHandler, FileHandler, Formatter
from optparse import OptionParser

from hwtest.contrib.persist import Persist

from hwtest import VERSION
from hwtest.config import Config
from hwtest.plugin import PluginManager
from hwtest.reactor import Reactor


class Application(object):

    def __init__(self, config_file, data_dir, log_handlers=None,
                 log_level=None):

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
        self.reactor = Reactor()

        # Persist setup
        persist_filename = os.path.join(data_dir, "data.bpickle")
        self.persist = self._get_persist(persist_filename)

        # Config setup
        self.config = Config()
        if os.path.exists(config_file):
            self.config.load_path(config_file)

        # Plugin manager setup
        self.plugin_manager = PluginManager(self.reactor,
            self.config, self.persist, persist_filename)

    def _get_persist(self, persist_filename):
        persist = Persist()

        if os.path.exists(persist_filename):
            persist.load(persist_filename)
        persist.save(persist_filename)
        return persist

    def run(self):
        try:
            self.reactor.run()
        except:
            logging.exception("Error running reactor.")
            raise


class ApplicationManager(object):

    application_factory = Application

    def parse_options(self, args):
        basename = os.path.basename(args[0])
        default_config_file = "/etc/hwtest.d/%s.conf" % basename
        default_data_dir = "~/.%s" % basename
        default_log_level = "critical"

        parser = OptionParser(version=VERSION)
        parser.add_option("-c", "--config-file", metavar="PATH",
                          default=default_config_file,
                          help="The file name of the configuration.")
        parser.add_option("-d", "--data-dir", metavar="PATH",
                          default=default_data_dir,
                          help="The directory to store data files.")
        parser.add_option("-l", "--log", metavar="FILE",
                          help="The file to write the log to.")
        parser.add_option("--log-level",
                          default=default_log_level,
                          help="One of debug, info, warning, error or critical.")
        return parser.parse_args(args)[0]

    def create_application(self, args=sys.argv):
        options = self.parse_options(args)

        log_level = logging.getLevelName(options.log_level.upper())
        log_handlers = []
        log_handlers.append(StreamHandler())
        if options.log:
            log_filename = options.log
            log_handlers.append(FileHandler(log_filename))

        data_dir = os.path.expanduser(options.data_dir)
        config_file = os.path.expanduser(options.config_file)

        return self.application_factory(
            config_file=config_file, data_dir=data_dir,
            log_handlers=log_handlers, log_level=log_level)
