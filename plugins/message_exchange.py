import time
import logging
import pprint
import StringIO

from hwtest.plugin import Plugin
from hwtest.transport import HTTPTransport
from hwtest.contrib import bpickle
from hwtest.log import format_delta


class MessageExchange(Plugin):
    transport_factory = HTTPTransport
    transport_url = 'http://192.168.99.193:8086/hwdb/submit-hardware-data'

    def __init__(self):
        self._transport = self.transport_factory(self.transport_url)

    def register(self, manager):
        self._manager = manager
        self._persist = manager.persist.root_at("message-exchange")
        self._manager.reactor.call_on("exchange", self.exchange)

    def exchange(self):
        report = self._manager.report

        # 'field.date_created':    u'2007-08-01',
        # 'field.format':          u'VERSION_1',
        # 'field.private':         u'',
        # 'field.contactable':     u'',
        # 'field.livecd':          u'',
        # 'field.submission_id':   u'unique ID 1',
        # 'field.emailaddress':    u'test@canonical.com',
        # 'field.distribution':    u'ubuntu',
        # 'field.distrorelease':   u'5.04',
        # 'field.architecture':    u'i386',
        # 'field.system':          u'HP 6543',
        # 'field.submission_data': data,
        # 'field.actions.upload':  u'Upload'}

        fields = {
            # XXX: these need to be pulled out of the message store
            'field.date_created':    u'2007-08-01',
            'field.format':          u'VERSION_1',
            'field.livecd':          u'',
            'field.private':         u'',
            'field.contactable':     u'',
            'field.distribution':    u'ubuntu',
            'field.distrorelease':   u'5.04',
            'field.architecture':    u'i386',
            'field.system':          u'HP 6543',
            'field.emailaddress':    u'test@canonical.com',
            'field.submission_id':   report.info['submission_id'],
            'field.actions.upload':  u'Upload'}

        form = []
        for k, v in fields.items():
            form.append((k, v.encode("utf-8")))

        payload = report.toxml()
        f = StringIO.StringIO(payload)
        f.name = 'hwdb.data'
        f.size = len(payload)
        form.append(('field.submission_data', f))

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Sending payload:\n%s", pprint.pformat(payload))

        start_time = time.time()

        ret = self._transport.exchange(form)

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Response headers:\n%s",
                          pprint.pformat(ret.headers.items()))

        if not ret:
            # HACK: this should return a useful error message
            self._manager.set_error("Communication failure")
            return

        header = ret.headers.get("x-launchpad-hwdb-submission")
        if header and "Error" in header:
            # HACK: this should return a useful error message
            self._manager.set_error("Submission failure")
            return

        response = ret.read()
        logging.info("Sent %d bytes and received %d bytes in %s.",
                     len(payload), len(response),
                     format_delta(time.time() - start_time))

        if not self._check_response(response):
            logging.exception("Server returned invalid data: %r" % ret)
            return None

        self._manager.set_error()

    def _check_response(self, response):
        """XXX"""
        return True


factory = MessageExchange
