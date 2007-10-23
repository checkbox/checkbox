import time
import pprint
import StringIO
import bz2
import logging

from datetime import datetime
from socket import gethostname

from hwtest.plugin import Plugin
from hwtest.transport import HTTPTransport
from hwtest.log import format_delta
from hwtest.lib.type import recursiveupdate

from hwtest.report import ReportManager
from hwtest.reports.data import DataReport
from hwtest.reports.summary import SummaryReport
from hwtest.reports.processor import ProcessorReport
from hwtest.reports.package import PackageReport
from hwtest.reports.hal import HalReport

class LaunchpadExchange(Plugin):

    transport_factory = HTTPTransport

    def __init__(self, config, report=None):
        super(LaunchpadExchange, self).__init__(config)
        self._transport = self.transport_factory(self.config.transport_url)
        self._report = {
            "summary": {
                "private": False,
                "contactable": False,
                "live_cd": False,
                "date_created": str(datetime.utcnow()).split(".")[0]},
            "hardware": {},
            "software": {},
            "tests": {}}
        self._form = [
            ('field.format', u'VERSION_1'),
            ('field.actions.upload', u'Upload')]

    def register(self, manager):
        super(LaunchpadExchange, self).register(manager)
        for (rt, rh) in [("exchange", self.exchange),
                         (("report", "architecture"), self.report_architecture),
                         (("report", "submission_id"), self.report_submission_id),
                         (("report", "system_id"), self.report_system_id),
                         (("report", "distribution"), self.report_distribution),
                         (("report", "package"), self.report_package),
                         (("report", "device"), self.report_device),
                         (("report", "processor"), self.report_processor),
                         (("report", "email"), self.report_email)]:
            self._manager.reactor.call_on(rt, rh)

    def report_architecture(self, message):
        self._report["summary"]["architecture"] = message

    def report_submission_id(self, message):
        logging.info("Submission ID: %s", message)
        self._form.append(('field.submission_key', message))

    def report_system_id(self, message):
        logging.info("System ID: %s", message)
        self._report["summary"]["system_id"] = message

    def report_distribution(self, message):
        self._report["software"]["lsbrelease"] = message
        self._report["summary"]["distribution"] = message["distributor-id"]
        self._report["summary"]["distroseries"] = message["release"]

    def report_package(self, message):
        self._report["software"]["packages"] = message

    def report_device(self, message):
        self._report["hardware"]["hal"] = message

    def report_processor(self, message):
        self._report["hardware"]["processors"] = message

    def report_processor(self, message):
        self._report["hardware"]["processors"] = message

    def report_email(self, message):
        self._form.append(('field.emailaddress', message))

    def exchange(self):
        # Combine summary with form data
        for k, v in self._report['summary'].items():
            form_field = k.replace("system_id", "system")
            self._form.append(('field.%s' % form_field, str(v).encode("utf-8")))

        # Prepare the report manager
        report_manager = ReportManager("system", "1.0")
        report_manager.add(DataReport())
        report_manager.add(SummaryReport())
        report_manager.add(ProcessorReport())
        report_manager.add(PackageReport())
        report_manager.add(HalReport())

        # bzip2 compress the payload and attach it to the form
        filename = '%s.xml.bz2' % str(gethostname())
        payload = report_manager.dumps(self._report).toprettyxml("")
        cpayload = bz2.compress(payload)
        f = StringIO.StringIO(cpayload)
        f.name = filename
        f.size = len(cpayload)
        self._form.append(('field.submission_data', f))

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Uncompressed payload length: %d", len(payload))

        start_time = time.time()
        ret = self._transport.exchange(self._form)
        if not ret:
            # HACK: this should return a useful error message
            self._manager.set_error("Communication failure")
            return

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Response headers:\n%s",
                          pprint.pformat(ret.headers.items()))

        headers = ret.headers.getheaders("x-launchpad-hwdb-submission")
        self._manager.set_error()
        for header in headers:
            if "Error" in header:
                # HACK: this should return a useful error message
                self._manager.set_error(header)
                logging.error(header)
                return

        response = ret.read()
        logging.info("Sent %d bytes and received %d bytes in %s.",
                     len(self._form), len(response),
                     format_delta(time.time() - start_time))


factory = LaunchpadExchange
