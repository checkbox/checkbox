#
# This file is part of Checkbox.
#
# Copyright 2011 Canonical Ltd.
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
class DeferredParser:
    """Parser for deferred dispatching of events."""

    def __init__(self, dispatcher, event_type="result"):
        self.dispatcher = dispatcher
        self.event_type = event_type

    def run(self, result):
        self.dispatcher.publishEvent(self.event_type, result)
