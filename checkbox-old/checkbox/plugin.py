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
import re

from checkbox.component import ComponentManager


class PluginManager(ComponentManager):
    """
    Plugin manager which extends the component to support the concepts
    of a reactor.
    """
    def __init__(self, config, reactor):
        super(PluginManager, self).__init__(config)
        self.reactor = reactor

        # Load sections
        self.sections = []
        section_names = self._config.get_defaults().plugins
        for section_name in re.split(r"\s+", section_names):
            section = self.load_section(section_name)
            self.sections.append(section)
            for module in section.load_modules():
                module.register(self)


class Plugin:
    """
    Plugin base class which should be inherited by each plugin
    implementation. This class extends the component to automatically
    call the run method if defined.
    """
    def register(self, manager):
        self._manager = manager
