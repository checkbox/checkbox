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
from gettext import gettext as _

from checkbox.properties import String
from checkbox.plugin import Plugin


class CategoryPrompt(Plugin):

    # Category of the system: desktop, laptop or server
    category = String(required=False)

    def register(self, manager):
        super(CategoryPrompt, self).register(manager)

        for (rt, rh) in [
             ("gather-persist", self.gather_persist),
             ("prompt-category", self.prompt_category)]:
            self._manager.reactor.call_on(rt, rh)

    def gather_persist(self, persist):
        self.persist = persist.root_at("category_prompt")

    def prompt_category(self, interface):
        category = self.persist.get("category") or self.category
        registry = self._manager.registry

        # Try to determine category from HAL formfactor
        if not category:
            formfactor = registry.hal.computer.system.formfactor
            if formfactor is not "unknown":
                category = formfactor

        # Try to determine category from dpkg architecture
        if not category:
            architecture = registry.dpkg.architecture
            if architecture is "sparc":
                category = "server"

        # Try to determine category from kernel version
        if not category:
            version = registry.hal.computer.system.kernel.version
            if str(version).endswith("-server"):
                category = "server"

        # Prompt for the category explicitly
        if not category:
            category = interface.show_category(_("Category"),
                _("Please select the category of your system."),
                category)

        self.persist.set("category", category)
        self._manager.reactor.fire("report-category", category)


factory = CategoryPrompt
