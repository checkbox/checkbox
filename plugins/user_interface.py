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
from checkbox.contrib.persist import Persist, MemoryBackend
from checkbox.plugin import Plugin
from checkbox.properties import Path, String
from checkbox.user_interface import PREV

import gettext
import posixpath

from gettext import gettext as _


class UserInterface(Plugin):

    # Module where the user interface implementation is defined.
    interface_module = String(default="checkbox.user_interface")

    # Class implementing the UserInterface interface.
    interface_class = String(default="UserInterface")

    # HACK: this is only a temporary workaround to internationalize the
    # user interface title and should be eventually removed.
    gettext.textdomain("checkbox")

    # Title of the user interface
    title = String(default=_("System Testing"))

    # Path where data files are stored.
    data_path = Path(required=False)

    @property
    def persist(self):
        if self._persist is None:
            self._persist = Persist(backend=MemoryBackend())

        return self._persist.root_at("user_interface")

    def register(self, manager):
        super(UserInterface, self).register(manager)

        self._persist = None

        self._manager.reactor.call_on("prompt-begin", self.prompt_begin)
        self._manager.reactor.call_on("stop", self.save_persist)
        self._manager.reactor.call_on("begin-persist", self.begin_persist)
        self._manager.reactor.call_on("run", self.run)
        self._manager.reactor.call_on("launchpad-report", self.launchpad_report)

        self._manager.reactor.call_on("set-progress",self.set_progress)
        self._manager.reactor.call_on("prompt-job",self.update_status, 101)

    def update_status(self, interface, job):
        #The UI can choose to implement this method to get
        #information about each job that completes
        interface.update_status(job)

    def begin_persist(self, persist):
        self._persist = persist

    def prompt_begin(self, interface):
        self._interface.ui_flags = self.persist.get("ui_flags", {})

    def save_persist(self, *args):
        self.persist.set("ui_flags", self._interface.ui_flags)
        self.persist.save()
    
    def set_progress(self, progress):
        self._interface.progress = progress
        
    def run(self):
        interface_module = __import__(self.interface_module,
            None, None, [''])
        interface_class = getattr(interface_module, self.interface_class)
        interface = interface_class(self.title, self.data_path)
        self._interface = interface

        event_types = [
             "prompt-begin",
             "prompt-gather",
             "prompt-jobs",
             "prompt-report",
             "prompt-exchange",
             "prompt-finish"]

        index = 0
        while index < len(event_types):
            event_type = event_types[index]
            self._manager.reactor.fire(event_type, interface)

            if interface.direction == PREV:
                if index > 0:
                    index -= 1
            else:
                index += 1

    def launchpad_report(self, launchpad_report):
        self._interface.report_url = "file://%s" % posixpath.abspath(launchpad_report)

factory = UserInterface
