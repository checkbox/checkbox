from hwtest.plugin import Plugin


class MessageExchange(Plugin):

    def __init__(self, transport):
        self._transport = transport

    def register(self, manager):
        self._manager = manager
        self._persist = manager.persist.root_at("message-exchange")
        self._manager.reactor.call_on("exchange", self.exchange, priority=500)

    def exchange(self):
        payload = self.make_payload()
        message_store = self._manager.message_store
        ret = self._transport.exchange(payload, message_store.get_secure_id())
        if ret:
            self._manager.set_error()
        else:
            # HACK: this should return a useful error message
            self._manager.set_error("Invalid Secure ID")

    def make_payload(self):
        message_store = self._manager.message_store
        messages = message_store.get_pending_messages()
        return {"messages": messages}
