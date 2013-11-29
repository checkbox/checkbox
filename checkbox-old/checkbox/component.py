#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

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
import itertools
import logging
import posixpath

from checkbox.lib.cache import cache
from checkbox.lib.path import path_expand_recursive

from checkbox.properties import List, String
from checkbox.variables import get_variables


class ComponentSection:
    """
    Component section which is essentially a container of modules. These
    map to the modules referenced in the configuration passed as argument
    to the constructor.
    """

    modules = List(type=String())
    whitelist = List(type=String(), default_factory=lambda:"")
    blacklist = List(type=String(), default_factory=lambda:"")

    def __init__(self, config, name):
        """
        Constructor which takes a configuration instance and name as
        argument. The former is expected to contain modules.
        """
        self._config = config
        self.name = name

        self.modules = config.modules
        self.whitelist = config.get("whitelist")
        self.blacklist = config.get("blacklist")

    @cache
    def get_names(self):
        """
        Get all the module names contained in the filenames or directories
        for this section.
        """
        whitelist_patterns = [re.compile(r"^%s$" % r) for r in self.whitelist]
        blacklist_patterns = [re.compile(r"^%s$" % r) for r in self.blacklist]

        # Determine names
        names = set()
        filenames = itertools.chain(*[path_expand_recursive(m)
            for m in self.modules])
        for filename in filenames:
            name = posixpath.basename(filename)
            if not name.endswith(".py") or name == "__init__.py":
                # Ignore silently
                continue

            name = name.replace(".py", "")
            if whitelist_patterns:
                if not [name for p in whitelist_patterns if p.match(name)]:
                    logging.info("Not whitelisted module: %s", name)
                    continue
            elif blacklist_patterns:
                if [name for p in blacklist_patterns if p.match(name)]:
                    logging.info("Blacklisted module: %s", name)
                    continue

            names.add(name)

        return list(names)

    def has_module(self, name):
        """
        Check if the given name is in this section.
        """
        return name in self.get_names()

    def load_module(self, name):
        """
        Load a single module by name from this section.
        """
        logging.info("Loading module %s from section %s",
            name, self.name)

        if not self.has_module(name):
            raise Exception("No such such module: %s" % name)

        filenames = itertools.chain(*[path_expand_recursive(m)
            for m in self.modules])
        for filename in filenames:
            if filename.endswith(".py") and posixpath.exists(filename):
                basename = posixpath.basename(filename)
                basename = basename.replace(".py", "")
                if basename == name:
                    globals = {}
                    exec(open(filename).read(), globals)
                    if "factory" not in globals:
                        raise Exception("Variable 'factory' not found in: %s" \
                            % filename)

                    module = globals["factory"]()
                    module.__module__ = name

                    config_name = "/".join([self.name, name])
                    config = self._config.parent.get_section(config_name)

                    # Set configuration values
                    variables = get_variables(module)
                    environ = dict([(k.lower(), v) for k, v in os.environ.items()])
                    for attribute, variable in variables.items():
                        if config and attribute.name in config:
                            value = config.get(attribute.name)
                            variable.set(value)
                        else:
                            value = variable.get()
                            if isinstance(value, str):
                                value = value % environ
                                variable.set(value)
                            elif isinstance(value, list):
                                value = [v % environ for v in value]
                                variable.set(value)

                    # Check required attributes
                    for attribute, variable in variables.items():
                        value = variable.get()
                        if value is None and variable._required:
                            raise Exception("Configuration '%s' missing " \
                                "required attribute: %s" \
                                % (config_name, attribute.name))

                    return module

        raise Exception("Failed to find module '%s' in: %s" % (name, filenames))

    def load_modules(self):
        """
        Load all modules contained in this section.
        """
        modules = []
        for name in self.get_names():
            module = self.load_module(name)
            modules.append(module)

        return modules


class ComponentManager:
    """
    Component manager which is essentially a container of sections.
    """

    _section_factory = ComponentSection

    def __init__(self, config):
        """
        Constructor which takes a configuration instance as argument. This
        will be used to load sections by name.
        """
        self._config = config

    def load_section(self, name):
        """
        Load a section by name which must correspond to a module in the
        configuration instance pased as argument to the constructor.
        """
        logging.info("Loading component section %s", name)
        config = self._config.get_section(name)
        return self._section_factory(config, name)
