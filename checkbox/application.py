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
import os
import sys
import logging
import posixpath

from gettext import gettext as _

from optparse import OptionParser

from checkbox.lib.config import Config
from checkbox.lib.environ import get_variable
from checkbox.lib.log import set_logging
from checkbox.lib.safe import safe_make_directory
from checkbox.lib.text import split

from checkbox.plugin import PluginManager
from checkbox.reactor import Reactor


class Application:

    reactor_factory = Reactor

    def __init__(self, config):
        self._config = config
        self.reactor = self.reactor_factory()

        # Plugin manager setup
        self.plugin_manager = PluginManager(self._config,
            self.reactor)

    def run(self):
        try:
            self.reactor.run()
        except:
            logging.exception("Error running reactor.")
            raise


class ApplicationManager:

    application_factory = Application

    default_log = os.path.join(get_variable("CHECKBOX_DATA", "."), "checkbox.log")
    default_log_level = "info"

    def parse_options(self, args):
        usage = _("Usage: checkbox [OPTIONS]")
        parser = OptionParser(usage=usage)
        parser.add_option("--version",
                          action="store_true",
                          help=_("Print version information and exit."))
        parser.add_option("-l", "--log",
                          metavar="FILE",
                          default=self.default_log,
                          help=_("The file to write the log to."))
        parser.add_option("--log-level",
                          default=self.default_log_level,
                          help=_("One of debug, info, warning, error or critical."))
        parser.add_option("-c", "--config",
                          action="append",
                          type="string",
                          default=[],
                          help=_("Configuration override parameters."))
        parser.add_option("-b", "--blacklist",
                          help=_("Shorthand for --config=.*/jobs_info/blacklist."))
        parser.add_option("-B", "--blacklist-file",
                          help=_("Shorthand for --config=.*/jobs_info/blacklist_file."))
        parser.add_option("-w", "--whitelist",
                          help=_("Shorthand for --config=.*/jobs_info/whitelist."))
        parser.add_option("-W", "--whitelist-file",
                          help=_("Shorthand for --config=.*/jobs_info/whitelist_file."))
        return parser.parse_args(args)

    def create_application(self, args=sys.argv):
        # Create data directory
        data_directory = get_variable("CHECKBOX_DATA", ".")
        safe_make_directory(data_directory)

        # Prepend environment options
        string_options = get_variable("CHECKBOX_OPTIONS", "")
        args[:0] = split(string_options)
        (options, args) = self.parse_options(args)

        # Replace shorthands
        for shorthand in "blacklist", "blacklist_file", "whitelist", "whitelist_file":
            key = ".*/jobs_info/%s" % shorthand
            value = getattr(options, shorthand)
            if value:
                options.config.append("=".join([key, value]))

        # Set logging early
        set_logging(options.log_level, options.log)

        # Config setup
        if len(args) != 2:
            sys.stderr.write(_("Missing configuration file as argument.\n"))
            sys.exit(1)

        config = Config()
        config_filename = posixpath.expanduser(args[1])
        config.read_filename(config_filename)
        config.read_configs(options.config)

        section_name = "checkbox/plugins/client_info"
        section = config.get_section(section_name)
        if not section:
            section = config.add_section(section_name)
        section.set("name", posixpath.basename(args[1]) \
            .replace(".ini", ""))
        section.set("version", config.get_defaults().version)

        # Check options
        if options.version:
            print(config.get_defaults().version)
            sys.exit(0)

        return self.application_factory(config)
