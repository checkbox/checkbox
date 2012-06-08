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
import re
import logging

from configparser import ConfigParser

from checkbox.lib.text import split


class IncludeDict(dict):

    def __init__(self, parser):
        super(IncludeDict, self).__init__()
        self._parser = parser

        for (key, value) in os.environ.items():
            if key.startswith("CHECKBOX"):
                super(IncludeDict, self).__setitem__(key.lower(), value)

    def __setitem__(self, key, value):
        if key == "includes":
            if isinstance(value, list):
                value = value[0]
            for path in split(value):
                path = self._parser._interpolation.before_get(
                    self._parser, "DEFAULT", None, path, self)
                path = os.path.expanduser(path)
                if not os.path.exists(path):
                    raise Exception("No such configuration file: %s" % path)
                if os.path.isdir(path):
                    logging.info("Parsing config filenames from directory: %s",
                        path)
                    for dirpath, dirnames, filenames in os.walk(path):
                        for filename in filenames:
                            path = os.path.join(dirpath, filename)
                            self._parser.read(path)
                else:
                    logging.info("Parsing config filename: %s", path)
                    self._parser.read(path)

        # Environment has precedence over configuration
        elif not key.startswith("CHECKBOX") or key.upper() not in os.environ:
            super(IncludeDict, self).__setitem__(key, value)


class ConfigSection:

    def __init__(self, parent, name, attributes={}):
        self.parent = parent
        self.name = name
        self.attributes = {}
        for key, value in attributes.items():
            self.attributes[key] = re.sub("\n\.\n", "\n\n", value)

    def __getattr__(self, name):
        if name in self.attributes:
            return self.get(name)

        raise AttributeError(name)

    def __contains__(self, name):
        return name in self.attributes

    def get(self, name):
        return self.attributes.get(name, "")

    def set(self, name, value):
        self.parent._parser.set(self.name, name, value)
        self.attributes[name] = value


class ConfigDefaults(ConfigSection):

    def __getattr__(self, name):
        if name in self.attributes:
            return self.get(name)

        raise AttributeError(name)

    def get(self, name):
        name_upper = name.upper()
        if not name_upper.startswith("CHECKBOX") or name_upper not in os.environ:
            return super(ConfigDefaults, self).get(name)
        else:
            return os.environ[name_upper]


class Config:

    def __init__(self):
        self._parser = ConfigParser(empty_lines_in_values=False)
        self._parser._defaults = IncludeDict(self._parser)

        # Copy attributes from the parser to avoid one additional
        # function call on each access.
        for attr in ["has_section", "remove_section"]:
            setattr(self, attr, getattr(self._parser, attr))

    def read_configs(self, configs):
        for config in configs:
            match = re.match("(.*)/([^/]+)=(.*)", config)
            if not match:
                raise Exception("Invalid config string: %s" % config)

            (name, option, value) = match.groups()

            # Match section names
            name_regex = re.compile(name)
            sections = [section for section in self._parser.sections()
                        if name_regex.match(section)]

            if not sections:
                self._parser.add_section(name)
                sections.append(name)

            for section in sections:
                logging.debug('Setting configuration parameter: '
                              '%(section)s/%(option)s = %(value)s'
                              % {'section': section,
                                 'option': option,
                                 'value': value})
                self._parser.set(section, option, value)

    def read_file(self, file, filename="<stream>"):
        logging.info("Reading configurations from: %s", filename)

        self._parser.read_file(file, filename)

    def read_filename(self, filename):
        if not os.path.exists(filename):
            raise Exception("No such configuration file: %s" % filename)

        file = open(filename, "r")
        return self.read_file(file, filename)

    def get_defaults(self):
        attributes = self._parser.defaults()
        return ConfigDefaults(self, 'DEFAULT', attributes)

    def get_section(self, name):
        if self._parser.has_section(name):
            attributes = dict(self._parser.items(name))
            return ConfigSection(self, name, attributes)

        return None

    def get_section_names(self):
        return self._parser.sections()

    def add_section(self, name):
        self._parser.add_section(name)
        return self.get_section(name)
