from hwtest.plugin import Plugin
from hwtest.reports.launchpad_report import LaunchpadReportManager


class LaunchpadReport(Plugin):

    required_attributes = ["cache_file"]

    def register(self, manager):
        super(LaunchpadReport, self).register(manager)
        self._report = {
            "summary": {
                "private": False,
                "contactable": False,
                "live_cd": False},
            "hardware": {},
            "software": {},
            "questions": []}

        # Launchpad report should be generated last.
        for (rt, rh, rp) in [
             ("report", self.report, 100),
             (("report", "client"), self.report_client, 0),
             (("report", "datetime"), self.report_datetime, 0),
             (("report", "architecture"), self.report_architecture, 0),
             (("report", "system_id"), self.report_system_id, 0),
             (("report", "distribution"), self.report_distribution, 0),
             (("report", "devices"), self.report_devices, 0),
             (("report", "packages"), self.report_packages, 0),
             (("report", "processors"), self.report_processors, 0),
             (("report", "questions"), self.report_questions, 0)]:
            self._manager.reactor.call_on(rt, rh, rp)

    def report_client(self, message):
        self._report["summary"]["client"] = message

    def report_datetime(self, message):
        self._report["summary"]["date_created"] = message

    def report_architecture(self, message):
        self._report["summary"]["architecture"] = message

    def report_system_id(self, message):
        self._report["summary"]["system_id"] = message

    def report_distribution(self, message):
        self._report["software"]["lsbrelease"] = dict(message)
        self._report["summary"]["distribution"] = message.distributor_id
        self._report["summary"]["distroseries"] = message.release

    def report_devices(self, message):
        self._report["hardware"]["hal"] = message

    def report_packages(self, message):
        self._report["software"]["packages"] = message

    def report_processors(self, message):
        self._report["hardware"]["processors"] = message

    def report_questions(self, message):
        self._report["questions"].extend(message)

    def report(self):
        # Prepare the payload and attach it to the form
        report_manager = LaunchpadReportManager("system", "1.0")
        payload = report_manager.dumps(self._report).toprettyxml("")

        cache_file = self.config.cache_file
        file(cache_file, "w").write(payload)
        self._manager.reactor.fire(("report", "launchpad"), cache_file)


factory = LaunchpadReport
