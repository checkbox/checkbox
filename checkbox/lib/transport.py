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
import logging

import os
import re
import stat
import sys

import email.generator
import http.client
import mimetypes
import socket
import ssl
import urllib.request, urllib.parse, urllib.error


class ProxyHTTPConnection(http.client.HTTPConnection):

    _ports = {"http": http.client.HTTP_PORT, "https": http.client.HTTPS_PORT}

    def request(self, method, url, body=None, headers={}):
        #request is called before connect, so can interpret url and get
        #real host/port to be used to make CONNECT request to proxy
        scheme, rest = urllib.parse.splittype(url)
        if scheme is None:
            raise ValueError("unknown URL type: %s" % url)
        #get host
        host, rest = urllib.parse.splithost(rest)
        #try to get port
        host, port = urllib.parse.splitport(host)
        #if port is not defined try to get from scheme
        if port is None:
            try:
                port = self._ports[scheme]
            except KeyError:
                raise ValueError("unknown protocol for: %s" % url)
        else:
            port = int(port)

        self._real_host = host
        self._real_port = port
        http.client.HTTPConnection.request(self, method, url, body, headers)

    def connect(self):
        http.client.HTTPConnection.connect(self)
        #send proxy CONNECT request
        self.send((
            "CONNECT %s:%d HTTP/1.0\r\n\r\n" % (self._real_host, self._real_port)
            ).encode("ascii"))
        #expect a HTTP/1.0 200 Connection established
        response = self.response_class(self.sock, method=self._method)
        (version, code, message) = response._read_status()
        #probably here we can handle auth requests...
        if code != 200:
            #proxy returned and error, abort connection, and raise exception
            self.close()
            raise socket.error("Proxy connection failed: %d %s" % (code, message.strip()))
        #eat up header block from proxy....
        while True:
            #should not use directly fp probably
            line = response.fp.readline()
            if line == b"\r\n":
                break


class ProxyHTTPSConnection(ProxyHTTPConnection):

    default_port = http.client.HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None, strict=None):
        ProxyHTTPConnection.__init__(self, host, port)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        ProxyHTTPConnection.connect(self)
        self.sock = ssl.wrap_socket(self.sock, self.key_file, self.cert_file)


class VerifiedHTTPSConnection(http.client.HTTPSConnection):

    # Compatibility layer with Python 2.5
    timeout = None
    _tunnel_host = None

    def match_name(self, name):
        parts = []
        for fragment in name.split(r"."):
            if fragment == "*":
                parts.append(".+")
            else:
                fragment = re.escape(fragment)
                parts.append(fragment.replace(r"\*", ".*"))
        return re.match(r"\A" + r"\.".join(parts) + r"\Z", self.host, re.IGNORECASE)

    def verify_cert(self, cert):
        # verify that the hostname matches that of the certificate
        if cert:
            san = cert.get("subjectAltName", ())
            for key, value in san:
                if key == "DNS" and self.match_name(value):
                    return True

            if not san:
                for subject in cert.get("subject", ()):
                    for key, value in subject:
                        if key == "commonName" and self.match_name(value):
                            return True

        return False

    def connect(self):
        # overrides the version in httplib so that we do
        #    certificate verification
        sock = socket.create_connection((self.host, self.port), self.timeout)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()

        # wrap the socket using verification with the root
        #    certs in trusted_root_certs
        self.sock = ssl.wrap_socket(sock,
            self.key_file,
            self.cert_file,
            cert_reqs=ssl.CERT_REQUIRED,
            ca_certs="/etc/ssl/certs/ca-certificates.crt")

        #if not self.verify_cert(self.sock.getpeercert()):
        #    raise ValueError(
        #        "Failed to verify cert for hostname: %s" % self.host)


class HTTPTransport:
    """Transport makes a request to exchange message data over HTTP."""

    def __init__(self, url):
        self.url = url

        proxies = urllib.request.getproxies()
        self.http_proxy = proxies.get("http")
        self.https_proxy = proxies.get("https")

    def _unpack_host_and_port(self, string):
        scheme, rest = urllib.parse.splittype(string)
        host, rest = urllib.parse.splithost(rest)
        host, port = urllib.parse.splitport(host)
        if port is not None:
            port = int(port)

        return (host, port)

    def _get_connection(self, timeout=0):
        if timeout:
            socket.setdefaulttimeout(timeout)

        scheme, rest = urllib.parse.splittype(self.url)
        if scheme == "http":
            if self.http_proxy:
                host, port = self._unpack_host_and_port(self.http_proxy)
            else:
                host, port = self._unpack_host_and_port(self.url)

            connection = http.client.HTTPConnection(host, port)
        elif scheme == "https":
            if self.https_proxy:
                host, port = self._unpack_host_and_port(self.https_proxy)
                connection = ProxyHTTPSConnection(host, port)
            else:
                host, port = self._unpack_host_and_port(self.url)
                connection = VerifiedHTTPSConnection(host, port)
        else:
            raise Exception("Unknown URL scheme: %s" % scheme)

        return connection

    def _encode_multipart_formdata(self, fields=[], files=[]):
        boundary = email.generator._make_boundary().encode("ascii")

        lines = []
        for (key, value) in fields:
            lines.append(b"--" + boundary)
            lines.append(b"Content-Disposition: form-data; name=\"" + key + b"\"")
            lines.append(b"")
            lines.append(value)

        for (key, file) in files:
            if hasattr(file, "size"):
                length = file.size
            else:
                length = os.fstat(file.fileno())[stat.ST_SIZE]

            content_type = mimetypes.guess_type(file.name)[0]
            if content_type:
                content_type = content_type.encode("ascii")
            else:
                content_type = b"application/octet-stream"

            filename = os.path.basename(file.name)
            filename = filename.encode("utf-8")

            lines.append(b"--" + boundary)
            lines.append(b"Content-Disposition: form-data; name=\"" + key + b"\"; filename=\"" + filename + b"\"")
            lines.append(b"Content-Type: " + content_type)
            lines.append(b"Content-Length: " + str(length).encode("ascii"))
            lines.append(b"")

            if hasattr(file, "seek"):
                file.seek(0)
            lines.append(file.read())

        lines.append(b"--" + boundary + b"--")
        lines.append(b"")

        content_type = b"multipart/form-data; boundary=" + boundary
        body = b"\r\n".join(lines)

        return content_type, body

    def _encode_body(self, body=None):
        fields = []
        files = []

        content_type = b"application/octet-stream"
        if body is not None and type(body) != bytes:
            if hasattr(body, "items"):
                body = list(body.items())
            else:
                try:
                    if len(body) and not isinstance(body[0], tuple):
                        raise TypeError
                except TypeError:
                    ty, va, tb = sys.exc_info()
                    raise TypeError("Invalid non-string sequence or mapping").with_traceback(tb)

            for key, value in body:
                key = key.encode("ascii")
                if hasattr(value, "read"):
                    files.append((key, value))
                else:
                    value = value.encode("utf-8")
                    fields.append((key, value))

            if files:
                content_type, body = self._encode_multipart_formdata(
                    fields, files)
            elif fields:
                content_type = b"application/x-www-form-urlencoded"
                body = urllib.parse.urlencode(fields).encode("utf-8")
            else:
                body = b""

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
            try:
                response = connection.getresponse()
            except http.client.BadStatusLine:
                logging.warning("Service unavailable on %s", self.url)
            else:
                if response.status == http.client.FOUND:
                    # TODO prevent infinite redirect loop
                    self.url = response.getheader('location')
                    response = self.exchange(body, headers, timeout)

        return response
