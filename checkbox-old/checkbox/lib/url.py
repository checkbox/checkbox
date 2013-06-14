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
import urllib.parse


def parse_url(url):
    scheme, host, path, params, query, fragment = urllib.parse.urlparse(url)

    if "@" in host:
        username, host = host.rsplit("@", 1)
        if ":" in username:
            username, password = username.split(":", 1)
        else:
            password = None
    else:
        username = password = None

    if ":" in host:
        host, port = host.split(":")
        assert port.isdigit()
        port = int(port)
    else:
        port = None

    return scheme, username, password, host, port, path, params, query, fragment
