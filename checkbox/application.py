#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
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
import os
import sys
import logging

from gettext import gettext as _

from logging import StreamHandler, FileHandler, Formatter
from optparse import OptionParser

from checkbox.contrib import bpickle_registry

from checkbox.config import Config
from checkbox.plugin import PluginManager
from checkbox.reactor import Reactor
from checkbox.registry import RegistryManager


class Application(object):

    reactor_factory = Reactor

    def __init__(self, config):
        self.config = config
        self.reactor = self.reactor_factory()

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

    default_log_level = "critical"

    def parse_options(self, args):
        parser = OptionParser()
        parser.add_option("--version",
                          action="store_true",
                          help=_("Print version information and exit."))
        parser.add_option("-l", "--log",
                          metavar="FILE",
                          help=_("The file to write the log to."))
        parser.add_option("--log-level",
                          default=self.default_log_level,
                          help=_("One of debug, info, warning, error or critical."))
        parser.add_option("-c", "--config",
                          action="append",
                          type="string",
                          default=[],
                          help=_("Configuration override parameters."))
        return parser.parse_args(args)

    def create_application(self, args=sys.argv):
        (options, args) = self.parse_options(args)

        log_level = logging.getLevelName(options.log_level.upper())
        log_handlers = []
        if options.log:
            log_filename = options.log
            log_handlers.append(FileHandler(log_filename))
        else:
            log_handlers.append(StreamHandler())

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
        if len(args) != 2:
            sys.stderr.write(_("Missing configuration file as argument.\n"))
            sys.exit(1)

        config_file = os.path.expanduser(args[1])
        config = Config(config_file, options.config)

        # Check options
        if options.version:
            print config.get_defaults().version
            sys.exit(0)

        return self.application_factory(config)
