import time
import pprint
import bz2
import logging

from StringIO import StringIO
from datetime import datetime
from socket import gethostname

from hwtest.log import format_delta
from hwtest.plugin import Plugin
from hwtest.reports.launchpad_report import LaunchpadReportManager
from hwtest.transport import HTTPTransport


class LaunchpadExchange(Plugin):

    def __init__(self, config):
        super(LaunchpadExchange, self).__init__(config)
        self._report = {
            "summary": {
                "private": False,
                "contactable": False,
                "live_cd": False,
                "date_created": str(datetime.utcnow()).split(".")[0]},
            "hardware": {},
            "software": {},
            "questions": []}
        self._form = {
            "field.format": u'VERSION_1',
            "field.actions.upload": u'Upload'}

    def register(self, manager):
        super(LaunchpadExchange, self).register(manager)
        for (rt, rh) in [("exchange", self.exchange),
                         (("report", "architecture"), self.report_architecture),
                         (("report", "submission_id"), self.report_submission_id),
                         (("report", "system_id"), self.report_system_id),
                         (("report", "distribution"), self.report_distribution),
                         (("report", "device"), self.report_device),
                         (("report", "processor"), self.report_processor),
                         (("report", "email"), self.report_email),
                         (("report", "questions"), self.report_questions)]:
            self._manager.reactor.call_on(rt, rh)

    def report_architecture(self, message):
        self._report["summary"]["architecture"] = message

    def report_submission_id(self, message):
        logging.info("Submission ID: %s", message)
        self._form["field.submission_key"] = message

    def report_system_id(self, message):
        logging.info("System ID: %s", message)
        self._report["summary"]["system_id"] = message

    def report_distribution(self, message):
        self._report["software"]["lsbrelease"] = dict(message)
        self._report["summary"]["distribution"] = message.distributor_id
        self._report["summary"]["distroseries"] = message.release

    def report_device(self, message):
        self._report["hardware"]["hal"] = message

    def report_processor(self, message):
        self._report["hardware"]["processors"] = message

    def report_email(self, message):
        self._form["field.emailaddress"] = message

    def report_questions(self, message):
        self._report["questions"] = message

    def exchange(self):
        # Combine summary with form data
        form = dict(self._form)
        for k, v in self._report['summary'].items():
            form_field = k.replace("system_id", "system")
            form["field.%s" % form_field] = str(v).encode("utf-8")

        # Prepare the payload and attach it to the form
        report_manager = LaunchpadReportManager("system", "1.0")
        payload = report_manager.dumps(self._report).toprettyxml("")
        cpayload = bz2.compress(payload)
        f = StringIO(cpayload)
        f.name = '%s.xml.bz2' % str(gethostname())
        f.size = len(cpayload)
        form["field.submission_data"] = f

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Uncompressed payload length: %d", len(payload))

        self._manager.set_error()
        start_time = time.time()
        transport = HTTPTransport(self.config.transport_url)
        ret = transport.exchange(form)
        if not ret:
            # HACK: this should return a useful error message
            self._manager.set_error("Communication failure.")
            return

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Response headers:\n%s",
                          pprint.pformat(ret.headers.items()))

        headers = ret.headers.getheaders("x-launchpad-hwdb-submission")
        if not headers:
            self._manager.set_error("Information was not posted to Launchpad.")
            return

        for header in headers:
            if "Error" in header:
                # HACK: this should return a useful error message
                self._manager.set_error(header)
                logging.error(header)
                return

        response = ret.read()
        logging.info("Sent %d bytes and received %d bytes in %s.",
                     f.size, len(response),
                     format_delta(time.time() - start_time))


factory = LaunchpadExchange
