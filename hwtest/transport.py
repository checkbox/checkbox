import logging
import urllib2

from hwtest import API, VERSION
from hwtest.constants import MESSAGE_API_HEADER


class HTTPTransport(object):
    """Transport makes a request to exchange message data over HTTP."""

    def __init__(self, url, pubkey=None):
        self._url = url
        self._pubkey = pubkey

    def get_url(self):
        return self._url

    def _post(self, form):
        opener = urllib2.build_opener()
        opener.addheaders = [(MESSAGE_API_HEADER, API),
                             ("User-Agent", "hwtest/%s" % (VERSION,))]
        ret = opener.open(self._url, form)
        return ret

    def exchange(self, form):
        """Exchange message data with the server.

        THREAD SAFE (HOPEFULLY)
        """
        try:
            ret = self._post(form)
        except:
            logging.exception("Error contacting the server")
            return None

        if ret.code != 200:
            logging.error("Server returned non-expected result: %d" % ret.code)
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

