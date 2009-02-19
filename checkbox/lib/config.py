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
import posixpath

from ConfigParser import ConfigParser


class IncludeDict(dict):

    def __init__(self, parser):
        super(IncludeDict, self).__init__()
        self._parser = parser

        for (key, value) in os.environ.items():
            super(IncludeDict, self).__setitem__(key.lower(), value)

    def __setitem__(self, key, value):
        if key == "includes":
            for path in re.split(r"\s*,?\s+", value):
                path = self._parser._interpolate("DEFAULT", None, path, self)
                path = posixpath.expanduser(path)
                if not posixpath.exists(path):
                    raise Exception, "No such configuration file: %s" % path
                if posixpath.isdir(path):
                    logging.info("Parsing config filenames from directory: %s",
                        path)
                    def walk_func(arg, directory, names):
                        for name in names:
                            path = posixpath.join(directory, name)
                            if not posixpath.isdir(path):
                                arg._parser.read(path)

                    posixpath.walk(path, walk_func, self)
                else:
                    logging.info("Parsing config filename: %s", path)
                    self._parser.read(path)

        # Environment has precedence over configuration
        elif key.upper() not in os.environ.keys():
            super(IncludeDict, self).__setitem__(key, value)


class ConfigSection(object):

    def __init__(self, parent, name, attributes={}):
        self.parent = parent
        self.name = name
        self.attributes = attributes

    def __getattr__(self, name):
        if name in self.attributes:
            return self.get(name)

        raise AttributeError, name

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

        raise AttributeError, name

    def get(self, name):
        return os.environ.get(name.upper()) \
            or os.environ.get(name.lower()) \
            or super(ConfigDefaults, self).get(name)


class Config(object):

    def __init__(self, path, configs=[]):
        self.path = path

        self._parser = ConfigParser()
        self._parser._defaults = IncludeDict(self._parser)

        if not posixpath.exists(path):
            raise Exception, "No such configuration file: %s" % path
        self._parser.read(path)

        for config in configs:
            match = re.match("(.*)/([^/]+)=(.*)", config)
            if not match:
                raise Exception, "Invalid config string: %s" % config

            (name, option, value) = match.groups()
            if not self._parser.has_section(name):
                self._parser.add_section(name)

            self._parser.set(name, option, value)

        # Copy attributes from the parser to avoid one additional
        # function call on each access.
        for attr in ["has_section", "remove_section"]:
            setattr(self, attr, getattr(self._parser, attr))

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
