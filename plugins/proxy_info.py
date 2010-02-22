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
import re

from checkbox.lib.environ import add_variable, get_variable

from checkbox.properties import String
from checkbox.plugin import Plugin


class ProxyInfo(Plugin):

    # HTTP proxy to use instead of the one specified in environment.
    http_proxy = String(required=False)

    # HTTPS proxy to use instead of the one specified in environment.
    https_proxy = String(required=False)

    def register(self, manager):
        super(ProxyInfo, self).register(manager)

        self.proxy = {}

        self._manager.reactor.call_on("report-gconf", self.report_gconf)
        self._manager.reactor.call_on("gather", self.gather, 100)

    def report_gconf(self, resources):
        proxy_pattern = re.compile(r"/system/(http_)?proxy/(?P<name>[^/]+)$")
        for resource in resources:
            match = proxy_pattern.match(resource["name"])
            if match:
                self.proxy[match.group("name")] = resource["value"]

    def gather(self):
        # Config has lowest precedence
        http_proxy = self.http_proxy
        https_proxy = self.https_proxy

        # Gconf has higher precedence
        proxy = self.proxy
        if proxy.get("use_http_proxy", False):
            if proxy.get("use_authentication", False):
                http_proxy = "http://%s:%s@%s:%s" % (
                    proxy["authentication_user"],
                    proxy["authentication_password"],
                    proxy["host"],
                    proxy["port"])
            elif "host" in proxy:
                http_proxy = "http://%s:%s" % (
                    proxy["host"],
                    proxy["port"])

            if proxy.get("use_same_proxy", False):
                https_proxy = http_proxy
            elif "secure_host" in proxy:
                https_proxy = "https://%s:%s" % (
                    proxy["secure_host"],
                    proxy["secure_port"])

        # Environment has highest precedence
        http_proxy = get_variable("http_proxy", http_proxy)
        https_proxy = get_variable("https_proxy", https_proxy)

        add_variable("http_proxy", http_proxy)
        add_variable("https_proxy", https_proxy)


factory = ProxyInfo
