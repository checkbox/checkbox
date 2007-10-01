import logging
import urllib2
import socket
import pprint

from hwtest import VERSION
from hwtest.contrib import urllib2_file


class HTTPTransport(object):
    """Transport makes a request to exchange message data over HTTP."""

    def __init__(self, url, pubkey=None):
        self._url = url
        self._pubkey = pubkey

    def get_url(self):
        return self._url

    def _post(self, form):
        """Actually POSTs the form to the server."""
        opener = urllib2.build_opener()
        opener.addheaders = [("User-Agent", "hwtest/%s" % (VERSION,))]
        ret = opener.open(self._url, form)
        return ret

    def exchange(self, form):
        """Exchange message data with the server.

        THREAD SAFE (HOPEFULLY)
        """
        socket.setdefaulttimeout(10)
        try:
            ret = self._post(form)
        except urllib2.URLError:
            logging.exception("Error contacting the server")
            return None
        except urllib2.HTTPError:
            logging.exception("Failure submitting data to server")
            logging.error("Response headers: %s",
                          pprint.pformat(ret.headers.items()))
            return None

        if ret.code != 200:
            logging.error("Server returned non-expected code: %d" % ret.code)
            return None

        return ret


class StubTransport(object):
    """Fake transport for testing purposes."""

    def __init__(self):
        self.payloads = []
        self.responses = []
        self.next_expected_sequence = 0
        self.extra = {}

    def get_url(self):
        return ""

    def exchange(self, payload, machine_id=None):
        self.payloads.append(payload)
        self.next_expected_sequence += len(payload.get("messages", []))
        result = {"next-expected-sequence": self.next_expected_sequence,
                  "messages": self.responses}
        result.update(self.extra)
        return result

