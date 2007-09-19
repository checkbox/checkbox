import logging
import pprint

from hwtest.plugin import Plugin
from hwtest.transport import HTTPTransport
from hwtest.contrib import bpickle


class MessageExchange(Plugin):
    transport_factory = HTTPTransport
    transport_url = 'https://launchpad.net/hwdb/submit-hardware-data'

    def __init__(self):
        self._transport = self.transport_factory(self.transport_url)

    def register(self, manager):
        self._manager = manager
        self._persist = manager.persist.root_at("message-exchange")
        self._manager.reactor.call_on("exchange", self.exchange)

    def exchange(self):
        payload = self.make_payload()
        message_store = self._manager.message_store
        spayload = bpickle.dumps(payload)
        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Sending payload:\n%s", pprint.pformat(payload))
        ret = self._transport.exchange(payload, message_store.get_secure_id())
        if not ret:
            # HACK: this should return a useful error message
            self._manager.set_error("Invalid Secure ID")
            return

        self._manager.set_error()

        try:
            response = bpickle.loads(ret)
            if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
                logging.debug("Received payload:\n%s",
                              pprint.pformat(response))
        except:
            logging.exception("Server returned invalid data: %r" % ret)
            return None

    def make_payload(self):
        message_store = self._manager.message_store
        messages = message_store.get_pending_messages()
        return {"messages": messages}


factory = MessageExchange
