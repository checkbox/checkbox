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
from checkbox.contrib.persist import Persist

from checkbox.properties import Path
from checkbox.plugin import Plugin


class PersistInfo(Plugin):

    # Filename where to persist information
    filename = Path(default="%(checkbox_data)s/plugins.bpickle")

    def register(self, manager):
        super(PersistInfo, self).register(manager)

        self.persist = None

        for (rt, rh) in [
             ("begin", self.begin),
             ("prompt-begin", self.begin),
             ("prompt-job", self.save),
             ("report-jobs", self.save)]:
            self._manager.reactor.call_on(rt, rh, -100)

        # Save persist data last
        self._manager.reactor.call_on("stop", self.save, 900)

        #This should fire first thing during the gathering phase.
        self._manager.reactor.call_on("gather", self.begin_gather, -900)

        #This should fire last during gathering (i.e. after
        #all other gathering callbacks are finished)
        self._manager.reactor.call_on("gather", self.end_gather, 900)

    def begin(self, interface=None):
        if self.persist is None:
            self.persist = Persist(self.filename)
            self._manager.reactor.fire("begin-persist", self.persist)

    def save(self, *args):
        # Flush data to disk
        if self.persist:
            self.persist.save()

    def begin_gather(self):
        #Speed boost during the gathering phase. Not critical data anyway.
        self.persist._backend.safe_file_closing = False

    def end_gather(self):
        #Back to saving data very carefully once gathering is done.
        self.persist._backend.safe_file_closing = True 

factory = PersistInfo
