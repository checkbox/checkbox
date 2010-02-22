#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
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
class Resource(dict):

    def __getattr__(self, name):
        return self.get(name)

    def __str__(self):
        strings = ["%s: %s" % (k, v) for k, v in self.iteritems()]

        return "\n".join(strings)

    def eval(self, source):
        try:
            value = eval(source, {}, self)
            if (type(value) in (bool, int) and value) \
               or (type(value) is tuple and True in value):
                return value
        except Exception:
            pass

        return None
