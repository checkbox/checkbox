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
import re
import logging
import posixpath


class RepositorySection(object):
    """
    Repository section which is essentially a container of entries. These
    map to the modules referenced in the configuration passed as argument
    to the constructor.
    """

    def __init__(self, config, name):
        """
        Constructor which takes a configuration instance and name as
        argument. The former is expected to contain directories and
        blacklist.
        """
        self._config = config
        self.name = name
        self._names = None

    @property
    def directories(self):
        """
        Directory contained for this sections.
        """
        directories = re.split(r"\s+", self._config.directories)
        return [posixpath.expanduser(d) for d in directories]

    def get_names(self):
        """
        Get all the module names contained in the directories for this
        section.
        """
        if self._names is None:
            if "whitelist" in self._config.attributes:
                self._names = re.split(r"\s+", self._config.whitelist)
            else:
                blacklist = []
                if "blacklist" in self._config.attributes:
                    blacklist = re.split(r"\s", self._config.blacklist)

                for directory in self.directories:
                    names = [p.replace('.py', '')
                        for p in os.listdir(directory)
                        if p.endswith('.py') and p != "__init__.py"]
                    self._names = list(set(names).difference(set(blacklist)))

        return self._names

    def get_arguments(self, name):
        config_name = "/".join([self.name, name])
        config = self._config.parent.get_section(config_name)

        return [config]

    def load_all(self):
        """
        Load all modules contained in this section.
        """
        entries = []
        for name in self.get_names():
            entries.append(self.load_entry(name))

        return entries

    def has_entry(self, name):
        """
        Check if the given name is in this section.
        """
        return name in self.get_names()

    def load_entry(self, name):
        """
        Load a single module by name from this section.
        """
        logging.info("Loading name %s from section %s",
            name, self.name)

        for directory in self.directories:
            path = posixpath.join(directory, "%s.py" % name)
            if posixpath.exists(path):
                globals = {}
                exec open(path) in globals
                if "factory" not in globals:
                    raise Exception, "Variable 'factory' not found: %s" % path

                arguments = self.get_arguments(name)
                return globals["factory"](*arguments)

        raise Exception, "Failed to find module '%s' in directories: %s" \
            % (name, self.directories)


class RepositoryManager(object):
    """
    Repository manager which is essentially a container of sections.
    """

    _section_factory = RepositorySection

    def __init__(self, config):
        """
        Constructor which takes a configuration instance as argument. This
        will be used to load sections by name.
        """
        self._config = config
        self._error = None

    def load_section(self, name):
        """
        Load a section by name which must correspond to an entry in the
        configuration instance pased as argument to the constructor.
        """
        logging.info("Loading repository section %s", name)
        config = self._config.get_section(name)
        return self._section_factory(config, name)

    def set_error(self, error=None):
        self._error = error

    def get_error(self):
        return self._error


class Repository(object):
    """
    Repository base class which should be inherited by each repository
    implementation.
    """

    required_attributes = []
    optional_attributes = []

    def __init__(self, config):
        """
        Constructor which takes a configuration instance as argument. This
        can be used to pass options to repositories.
        """
        self._config = config
        self._validate()

    def _validate(self):
        all_required_attributes = []
        all_optional_attributes = []

        cls = type(self)
        for cls_mro in cls.__mro__:
            for attr, descr in cls_mro.__dict__.iteritems():
                if attr == "required_attributes":
                    all_required_attributes.extend(descr)
                elif attr == "optional_attributes":
                    all_optional_attributes.extend(descr)

        if all_required_attributes and not self._config:
            raise Exception, \
                "Missing configuration section for required attributes: %s" \
                % ", ".join(all_required_attributes)

        if all_optional_attributes and not self._config:
            raise Exception, \
                "Missing configuration section for optional attributes: %s" \
                % ", ".join(all_optional_attributes)

        if not self._config:
            return

        for attribute in all_required_attributes:
            if attribute not in self._config.attributes:
                raise Exception, \
                    "Configuration section '%s' missing required attribute: %s" \
                    % (self._config.name, attribute)

        for attribute in all_optional_attributes:
            if attribute not in self._config.attributes:
                self._config.attributes[attribute] = None

        all_attributes = all_required_attributes \
            + all_optional_attributes \
            + self._config.parent.get_defaults().attributes.keys()
        for attribute in self._config.attributes.keys():
            if attribute not in all_attributes:
                logging.info("Configuration section '%s' "
                    "contains unknown attribute: %s",
                    self._config.name, attribute)
