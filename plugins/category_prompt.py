#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of HWTest.
#
# HWTest is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# HWTest is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with HWTest.  If not, see <http://www.gnu.org/licenses/>.
#
from gettext import gettext as _

from hwtest.plugin import Plugin


class CategoryPrompt(Plugin):

    optional_attributes = ["category"]

    def register(self, manager):
        super(CategoryPrompt, self).register(manager)
        self._category = self.config.category

        for (rt, rh) in [
             (("prompt", "category"), self.prompt_category)]:
            self._manager.reactor.call_on(rt, rh)

    def prompt_category(self, interface):
        registry = self._manager.registry

        # Try to determine category from HAL formfactor
        if not self._category:
            formfactor = registry.hal.computer.system.formfactor
            if formfactor is not "unknown":
                self._category = formfactor

        # Try to determine category from dpkg architecture
        if not self._category:
            architecture = registry.dpkg.architecture
            if architecture is "sparc":
                self._category = "server"

        # Try to determine category from kernel version
        if not self._category:
            version = registry.hal.computer.system.kernel.version
            if str(version).endswith("-server"):
                self._category = "server"

        self._category = interface.show_category(_("Category"),
            _("Please select the category of your hardware."),
            self._category)

        self._manager.reactor.fire(("interface", "category"), self._category)


factory = CategoryPrompt
