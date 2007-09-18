from cStringIO import StringIO
import time
import logging
import pprint

import pycurl

from hwtest.contrib import bpickle

from hwtest import API, VERSION
from hwtest.constants import MACHINE_ID_HEADER, MESSAGE_API_HEADER
from hwtest.log import format_delta


class HTTPTransport(object):
    """Transport makes a request to exchange message data over HTTP."""
    
    def __init__(self, url, pubkey=None):
        self._url = url
        self._pubkey = pubkey

    def get_url(self):
        return self._url

    def _curl(self, payload, machine_id):
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, self._url)
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.MAXREDIRS, 5)

        headers = ["%s: %s" % (MESSAGE_API_HEADER, API,),
                   "User-Agent: hwtest/%s" % (VERSION,),
                   "Content-Type: application/octet-stream"]
        if machine_id:
            headers.append("%s: %s" % (MACHINE_ID_HEADER, machine_id,))

        curl.setopt(pycurl.HTTPHEADER, headers)
        curl.setopt(pycurl.POST, True)

        # HACK: waiting for pubkey from IS team
        curl.setopt(pycurl.SSL_VERIFYHOST, 1)
        curl.setopt(pycurl.SSL_VERIFYPEER, False)

        if self._url.startswith("https") and self._pubkey is not None:
            curl.setopt(pycurl.CAINFO, self._pubkey)

        # HACK: curl can't get size if data has a \0
        curl.setopt(pycurl.POSTFIELDSIZE, len(payload))
        curl.setopt(pycurl.POSTFIELDS, payload)

        io = StringIO()
        curl.setopt(pycurl.WRITEFUNCTION, io.write)

        curl.perform()
        return curl, io.getvalue()

    def exchange(self, payload, machine_id=None):
        """Exchange message data with the server.

        THREAD SAFE (HOPEFULLY)
        """
        spayload = bpickle.dumps(payload)
        try:
            start_time = time.time()
            if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
                logging.debug("Sending payload:\n%s", pprint.pformat(payload))

            curly, data = self._curl(spayload, machine_id)
            logging.info("Sent %d bytes and received %d bytes in %s.",
                         len(spayload), len(data),
                         format_delta(time.time() - start_time))
        except:
            logging.exception("Error contacting the server")
            return None

        code = curly.getinfo(pycurl.RESPONSE_CODE)
        if code != 200:
            logging.error("Server returned non-expected result: %d" % (code,))
            return None

        try:
            response = bpickle.loads(data)
            if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
                logging.debug("Received payload:\n%s",
                              pprint.pformat(response))
        except:
            logging.exception("Server returned invalid data: %r" % data)
            return None

        return response


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
