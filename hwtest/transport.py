from cStringIO import StringIO
import time
import logging
import urllib2

import pycurl

from hwtest import API, VERSION
from hwtest.constants import MACHINE_ID_HEADER, MESSAGE_API_HEADER
from hwtest.log import format_delta
from hwtest.contrib import urllib2_file


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
        import pdb; pdb.set_trace()
        ret = opener.open(self._url, form)
        return ret

    def exchange(self, form):
        """Exchange message data with the server.

        THREAD SAFE (HOPEFULLY)
        """
        try:
            start_time = time.time()
            curly, data = self._post(form)
            logging.info("Sent %d bytes and received %d bytes in %s.",
                         666, len(data),
                         format_delta(time.time() - start_time))
        except:
            logging.exception("Error contacting the server")
            return None

        code = curly.getinfo(pycurl.RESPONSE_CODE)
        if code != 200:
            logging.error("Server returned non-expected result: %d" % (code,))
            return None

        return data


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

