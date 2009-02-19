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
from checkbox.contrib.persist import Persist

from checkbox.properties import Path
from checkbox.plugin import Plugin


class PersistInfo(Plugin):

    # E-mail address used to sign in to Launchpad.
    filename = Path(default="%(checkbox_data)s/plugins.bpickle")

    def register(self, manager):
        super(PersistInfo, self).register(manager)

        self.persist = None

        for (rt, rh) in [
             ("gather", self.gather),
             ("stop", self.stop)]:
            self._manager.reactor.call_on(rt, rh)

    def gather(self):
        self.persist = Persist(self.filename)
        self._manager.reactor.fire("gather-persist", self.persist)

    def stop(self):
        """Flush data to disk."""
        if self.persist:
            self.persist.save()


factory = PersistInfo
