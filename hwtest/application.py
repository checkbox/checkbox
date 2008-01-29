import os
import re
import sys
import logging

from gettext import gettext as _
from time import sleep

from logging import StreamHandler, FileHandler, Formatter
from optparse import OptionParser

from hwtest.contrib import bpickle_registry

from hwtest.defaults import CONFIG_FILE
from hwtest.config import Config
from hwtest.plugin import PluginManager
from hwtest.registry import RegistryManager
from hwtest.reactor import Reactor


class Application(object):

    def __init__(self, config):
        self.config = config

        # Reactor setup
        self.reactor = Reactor()

        # Registry manager setup
        self.registry = RegistryManager(self.config)

        # Plugin manager setup
        self.plugin_manager = PluginManager(self.config,
            self.registry, self.reactor)

    def run(self):
        try:
            bpickle_registry.install()
            self.reactor.run()
            bpickle_registry.uninstall()
        except:
            logging.exception("Error running reactor.")
            raise


class ApplicationManager(object):

    application_factory = Application

    def parse_options(self, args):
        name = os.path.basename(args[0])
        base_name = re.sub(r"(-gtk|-cli)$", "", name)

        default_config_file = CONFIG_FILE \
            % {"name": name, "base_name": base_name}
        default_log_level = "critical"
        default_delay = 0

        parser = OptionParser()
        parser.add_option("--version", action='store_true',
                          help=_("Print version information and exit."))
        parser.add_option("-c", "--config-file", metavar="PATH",
                          default=default_config_file,
                          help=_("The file name of the configuration."))
        parser.add_option("-l", "--log", metavar="FILE",
                          help=_("The file to write the log to."))
        parser.add_option("--log-level",
                          default=default_log_level,
                          help=_("One of debug, info, warning, error or critical."))
        parser.add_option("--delay",
                          default=default_delay,
                          type="int",
                          help=_("Delay before running the application."))
        return parser.parse_args(args)[0]

    def create_application(self, args=sys.argv):
        options = self.parse_options(args)

        log_level = logging.getLevelName(options.log_level.upper())
        log_handlers = []
        log_handlers.append(StreamHandler())
        if options.log:
            log_filename = options.log
            log_handlers.append(FileHandler(log_filename))

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

        # Config setup
        config_file = os.path.expanduser(options.config_file)
        config = Config(config_file)

        # Check options
        if options.version:
            print config.get_defaults().version
            sys.exit(0)

        if options.delay:
            sleep(options.delay)

        return self.application_factory(config)
