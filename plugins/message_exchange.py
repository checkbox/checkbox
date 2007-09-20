from hwtest.plugin import Plugin
from hwtest.transport import HTTPTransport


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
        payload = self._manager.report.toxml()
        secure_id = self._manager.report.info['submission_id']
        import pdb; pdb.set_trace()
        ret = self._transport.exchange(payload, secure_id)

        if ret:
            self._manager.set_error()
        else:
            # HACK: this should return a useful error message
            self._manager.set_error("Invalid Secure ID")


factory = MessageExchange
