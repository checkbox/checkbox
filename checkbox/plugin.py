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

from checkbox.repository import Repository, RepositoryManager


class PluginManager(RepositoryManager):
    """
    Plugin manager which extends the repository to support the concepts
    of a reactor.
    """

    def __init__(self, config, registry, reactor):
        super(PluginManager, self).__init__(config)
        self.registry = registry
        self.reactor = reactor

        # Load sections
        sections = self._config.get_defaults().plugins
        for section_name in re.split(r"\s+", sections):
            section = self.load_section(section_name)
            for module in section.load_all():
                module.register(self)


class Plugin(Repository):
    """
    Plugin base class which should be inherited by each plugin
    implementation. This class extends the repository to automatically
    call the run method if defined.
    """

    def register(self, manager):
        self._manager = manager
        if hasattr(self, "run"):
            manager.reactor.call_on("run", self.run)
