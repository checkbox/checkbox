#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
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
import logging

import os
import stat
import sys

import mimetools
import mimetypes
import socket
import urllib

from httplib import FakeSocket, HTTPConnection, HTTPSConnection


class ProxyHTTPConnection(HTTPConnection):

    _ports = {"http" : 80, "https" : 443}

    def request(self, method, url, body=None, headers={}):
        #request is called before connect, so can interpret url and get
        #real host/port to be used to make CONNECT request to proxy
        scheme, rest = urllib.splittype(url)
        if scheme is None:
            raise ValueError, "unknown URL type: %s" % url
        #get host
        host, rest = urllib.splithost(rest)
        #try to get port
        host, port = urllib.splitport(host)
        #if port is not defined try to get from scheme
        if port is None:
            try:
                port = self._ports[scheme]
            except KeyError:
                raise ValueError, "unknown protocol for: %s" % url
        self._real_host = host
        self._real_port = port
        HTTPConnection.request(self, method, url, body, headers)

    def connect(self):
        HTTPConnection.connect(self)
        #send proxy CONNECT request
        self.send("CONNECT %s:%d HTTP/1.0\r\n\r\n" % (self._real_host, self._real_port))
        #expect a HTTP/1.0 200 Connection established
        response = self.response_class(self.sock, strict=self.strict, method=self._method)
        (version, code, message) = response._read_status()
        #probably here we can handle auth requests...
        if code != 200:
            #proxy returned and error, abort connection, and raise exception
            self.close()
            raise socket.error, "Proxy connection failed: %d %s" % (code, message.strip())
        #eat up header block from proxy....
        while True:
            #should not use directly fp probablu
            line = response.fp.readline()
            if line == "\r\n":
                break


class ProxyHTTPSConnection(ProxyHTTPConnection):

    default_port = 443

    def __init__(self, host, port=None, key_file=None, cert_file=None, strict=None):
        ProxyHTTPConnection.__init__(self, host, port)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        ProxyHTTPConnection.connect(self)
        #make the sock ssl-aware
        ssl = socket.ssl(self.sock, self.key_file, self.cert_file)
        self.sock = FakeSocket(self.sock, ssl)


class HTTPTransport(object):
    """Transport makes a request to exchange message data over HTTP."""

    def __init__(self, url):
        self.url = url

        proxies = urllib.getproxies()
        self.http_proxy = proxies.get("http")
        self.https_proxy = proxies.get("https")

    def _unpack_host_and_port(self, string):
        scheme, rest = urllib.splittype(string)
        host, rest = urllib.splithost(rest)
        host, port = urllib.splitport(host)
        return (host, port)

    def _get_connection(self, timeout=0):
        if timeout:
            socket.setdefaulttimeout(timeout)

        scheme, rest = urllib.splittype(self.url)
        if scheme == "http":
            if self.http_proxy:
                host, port = self._unpack_host_and_port(self.http_proxy)
            else:
                host, port = self._unpack_host_and_port(self.url)

            connection = HTTPConnection(host, port)
        elif scheme == "https":
            if self.https_proxy:
                host, port = self._unpack_host_and_port(self.https_proxy)
                connection = ProxyHTTPSConnection(host, port)
            else:
                host, port = self._unpack_host_and_port(self.url)
                connection = HTTPSConnection(host, port)
        else:
            raise Exception, "Unknown URL scheme: %s" % scheme

        return connection

    def _encode_multipart_formdata(self, fields=[], files=[]):
        boundary = mimetools.choose_boundary()

        lines = []
        for (key, value) in fields:
            lines.append("--" + boundary)
            lines.append("Content-Disposition: form-data; name=\"%s\"" % key)
            lines.append("")
            lines.append(value)

        for (key, descriptor) in files:
            if hasattr(descriptor, "size"):
                length = descriptor.size
            else:
                length = os.fstat(descriptor.fileno())[stat.ST_SIZE]

            filename = os.path.basename(descriptor.name)
            if isinstance(filename, unicode):
                filename = filename.encode("UTF-8")

            lines.append("--" + boundary)
            lines.append("Content-Disposition: form-data; name=\"%s\"; filename=\"%s\""
                % (key, filename))
            lines.append("Content-Type: %s"
                % mimetypes.guess_type(filename)[0] or "application/octet-stream")
            lines.append("Content-Length: %s" % length)
            lines.append("")

            if hasattr(descriptor, "seek"):
                descriptor.seek(0)
            lines.append(descriptor.read())

        lines.append("--" + boundary + "--")
        lines.append("")

        content_type = "multipart/form-data; boundary=%s" % boundary
        body = "\r\n".join(lines)

        return content_type, body

    def _encode_body(self, body=None):
        fields = []
        files = []

        content_type = "application/octet-stream"
        if body is not None and type(body) != str:
            if hasattr(body, "items"):
                body = body.items()
            else:
                try:
                    if len(body) and not isinstance(body[0], tuple):
                        raise TypeError
                except TypeError:
                    ty, va, tb = sys.exc_info()
                    raise TypeError, \
                        "Invalid non-string sequence or mapping", tb

            for key, value in body:
                if hasattr(value, "read"):
                    files.append((key, value))
                else:
                    fields.append((key, value))

            if files:
                content_type, body = self._encode_multipart_formdata(fields,
                    files)
            elif fields:
                content_type = "application/x-www-form-urlencoded"
                body = urllib.urlencode(fields)
            else:
                body = ""

        return content_type, body

    def exchange(self, body=None, headers={}, timeout=0):
        headers = dict(headers)

        if body is not None:
            method = "POST"
            (content_type, body) = self._encode_body(body)
            if "Content-Type" not in headers:
                headers["Content-Type"] = content_type
            if "Content-Length" not in headers:
                headers["Content-Length"] = len(body)
        else:
            method = "GET"

        response = None
        connection = self._get_connection(timeout)

        try:
            connection.request(method, self.url, body, headers)
        except IOError:
            logging.warning("Can't connect to %s", self.url)
        except socket.error:
            logging.error("Error connecting to %s", self.url)
        except socket.timeout:
            logging.warning("Timeout connecting to %s", self.url)
        else:
            response = connection.getresponse()
            if response.status == 302:
                # TODO prevent infinite redirect loop
                self.url = self._get_location_header(response)
                response = self.exchange(body, headers, timeout)

        return response
