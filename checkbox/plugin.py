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
import re

from checkbox.repository import Repository, RepositoryManager, RepositorySection
from checkbox.contrib.persist import Persist


class PluginSection(RepositorySection):

    def __init__(self, *args, **kwargs):
        super(PluginSection, self).__init__(*args, **kwargs)

        self._persist = Persist(self._config.persist_filename)

    def get_arguments(self, name):
        """Add a rooted persist object to the parent arguments."""
        arguments = super(PluginSection, self).get_arguments(name)
        arguments.append(self._persist.root_at(name))

        return arguments

    def flush(self):
        """Flush data to disk."""
        self._persist.save()


class PluginManager(RepositoryManager):
    """
    Plugin manager which extends the repository to support the concepts
    of a reactor.
    """
    _section_factory = PluginSection

    def __init__(self, config, reactor, registry):
        super(PluginManager, self).__init__(config)
        self.reactor = reactor
        self.registry = registry

        # Load sections
        self.sections = []
        section_names = self._config.get_defaults().plugins
        for section_name in re.split(r"\s+", section_names):
            section = self.load_section(section_name)
            self.sections.append(section)
            for module in section.load_all():
                module.register(self)

    def flush(self):
        for section in self.sections:
            section.flush()


class Plugin(Repository):
    """
    Plugin base class which should be inherited by each plugin
    implementation. This class extends the repository to automatically
    call the run method if defined.
    """
    def __init__(self, config, persist):
        super(Plugin, self).__init__(config)
        self.persist = persist

    def register(self, manager):
        self._manager = manager
        if hasattr(self, "run"):
            manager.reactor.call_on("run", self.run)
