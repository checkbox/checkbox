from hwtest.plugin import Plugin
from hwtest.reports.launchpad_report import LaunchpadReportManager


class LaunchpadReport(Plugin):

    attributes = ["cache_file"]

    def __init__(self, *args, **kwargs):
        super(LaunchpadReport, self).__init__(*args, **kwargs)
        self._report = {
            "summary": {
                "private": False,
                "contactable": False,
                "live_cd": False},
            "hardware": {},
            "software": {},
            "questions": []}

    def register(self, manager):
        super(LaunchpadReport, self).register(manager)

        # Launchpad report should be generated last.
        for (rt, rh, rp) in [
             ("report", self.report, 100),
             (("report", "datetime"), self.report_datetime, 0),
             (("report", "architecture"), self.report_architecture, 0),
             (("report", "system_key"), self.report_system_key, 0),
             (("report", "distribution"), self.report_distribution, 0),
             (("report", "device"), self.report_device, 0),
             (("report", "processor"), self.report_processor, 0),
             (("report", "questions"), self.report_questions,0 )]:
            self._manager.reactor.call_on(rt, rh, rp)

    def report_datetime(self, message):
        self._report["summary"]["date_created"] = message

    def report_architecture(self, message):
        self._report["summary"]["architecture"] = message

    def report_system_key(self, message):
        self._report["summary"]["system_id"] = message

    def report_distribution(self, message):
        self._report["software"]["lsbrelease"] = dict(message)
        self._report["summary"]["distribution"] = message.distributor_id
        self._report["summary"]["distroseries"] = message.release

    def report_device(self, message):
        self._report["hardware"]["hal"] = message

    def report_processor(self, message):
        self._report["hardware"]["processors"] = message

    def report_questions(self, message):
        self._report["questions"].extend(message)

    def report(self):
        # Prepare the payload and attach it to the form
        report_manager = LaunchpadReportManager("system", "1.0")
        payload = report_manager.dumps(self._report).toprettyxml("")
        if self.config.cache_file:
            file(self.config.cache_file, "w").write(payload)

        self._manager.reactor.fire(("report", "launchpad"), payload)


factory = LaunchpadReport
