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
from time import sleep

from checkbox.properties import Float
from checkbox.plugin import Plugin


class DelayPrompt(Plugin):

    # Timeout for an initial delay
    timeout = Float(default=0.0)

    def register(self, manager):
        super(DelayPrompt, self).register(manager)

        # Force delay as early as possible
        sleep(self.timeout)


factory = DelayPrompt
