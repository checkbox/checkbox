import time
import pprint
import StringIO
import bz2
import md5
import logging

from operator import indexOf, itemgetter
from socket import gethostname

from hwtest.plugin import Plugin
from hwtest.transport import HTTPTransport
from hwtest.log import format_delta
from hwtest.report import Report
from hwtest.report_helpers import (createDevice, createElement,
    createProperty, createTypedElement)


class LaunchpadReport(Plugin):

    transport_factory = HTTPTransport

    def __init__(self, config, report=None):
        super(LaunchpadReport, self).__init__(config)
        self._report = report or Report()
        self._transport = self.transport_factory(self.config.transport_url)

    def register(self, manager):
        super(LaunchpadReport, self).register(manager)
        c = self._manager.reactor.call_on
        c(("report", "set-architecture"), self.set_architecture)
        c(("report", "set-email"), self.set_email)
        c(("report", "set-device-manager"), self.set_device_manager)
        c(("report", "set-distribution"), self.set_distribution)
        c(("report", "set-packages"), self.set_packages)
        c(("report", "set-processors"), self.set_processors)
        c(("report", "set-questions"), self.set_questions)

    def set_architecture(self, architecture):
        report = self._report
        if report.finalised:
            return

        report.info['architecture'] = architecture

    def set_email(self, email):
        report = self._report
        if report.finalised:
            return

        report.email = email

    def set_device_manager(self, device_manager):
        report = self._report
        if report.finalised:
            return

        hardware_element = createElement(report, 'hardware', report.root)
        report.hardware = hardware_element
        hal_element = createElement(report, 'hal', hardware_element)
        hal_element.setAttribute('version', str(device_manager.version))

        devices = device_manager.get_devices()
        for device in devices:
            id = indexOf(devices, device)
            device_element = createDevice(report, hal_element, id, device.udi,
                                  getattr(device.parent, 'id', None))
            properties_element = createElement(report, 'properties',
                device_element)
            for key, value in sorted(device.properties.iteritems(),
                                     key=itemgetter(0)):
                createProperty(report, properties_element, key, value)

        # Generate system fingerprint
        udi = '/org/freedesktop/Hal/devices/computer'
        computer = filter(lambda d: d.properties['info.udi'] == udi, devices)[0]

        fingerprint = md5.new()
        fingerprint.update(computer.properties['system.vendor'])
        fingerprint.update(computer.properties['system.product'])
        report.info['system_id'] = fingerprint.hexdigest()

    def set_distribution(self, distribution):
        report = self._report
        if report.finalised:
            return

        # Store summary information
        report.info['distribution'] = distribution['distributor-id']
        report.info['distroseries'] = distribution['release']

        # Store data in report
        software_element = getattr(report, 'software', None)
        if software_element is None:
            software_element = createElement(report, 'software', report.root)
            report.software = software_element
        createTypedElement(report, 'lsbrelease', software_element, None,
                           distribution, True)

    def set_packages(self, packages):
        report = self._report
        if report.finalised:
            return

        software_element = getattr(report, 'software', None)
        if software_element is None:
            software_element = createElement(report, 'software', report.root)
            report.software = software_element
        packages_element = createElement(report, 'packages', software_element)
        for package in packages:
            name = package.pop('name')
            createTypedElement(report, 'package', packages_element,
                               name, package, True)

    def set_processors(self, processors):
        report = self._report
        if report.finalised:
            return

        processors_element = createElement(report, 'processors', report.hardware)
        for processor in processors:
            createTypedElement(report, 'processor', processors_element,
            str(processors.index(processor)), processor.properties, True)

    def set_questions(self, questions):
        report = self._report
        if report.finalised:
            return

        for question in questions:
            tests_element = getattr(report, 'tests', None)
            if tests_element is None:
                tests_element = createElement(report, 'tests', report.root)
                report.tests = tests_element
            test_element = createElement(report, 'test', tests_element)
            createElement(report, 'suite', test_element, 'tool')
            createElement(report, 'name', test_element, question.name)
            createElement(report, 'description', test_element, question.description)
            createElement(report, 'command', test_element)
            createElement(report, 'architectures', test_element)
            createTypedElement(report, 'categories', test_element, None,
                question.categories, True, 'category')
            createElement(report, 'optional', test_element, question.optional)

            if question.answer:
                result_element = createElement(report, 'result', test_element)
                createElement(report, 'result_status', result_element,
                    question.answer.status)
                createElement(report, 'result_data', result_element,
                    question.answer.data)

    def exchange(self):
        report = self._report
        report.finalise()

        # 'field.date_created':    u'2007-08-01',
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

        form = []
        name_map = {'system_id': 'system'}

        for k, v in report.info.items():
            form_field = name_map.get(k, k)
            form.append(('field.%s' % form_field, str(v).encode("utf-8")))
 
        form.append(('field.format', u'VERSION_1'))
        form.append(('field.emailaddress', report.email))
        form.append(('field.actions.upload', u'Upload'))

        # Set the filename based on the hostname
        filename = '%s.xml.bz2' % str(gethostname())
        
        # bzip2 compress the payload and attach it to the form
        payload = report.toxml()
        cpayload = bz2.compress(payload)
        f = StringIO.StringIO(cpayload)
        f.name = filename
        f.size = len(cpayload)
        form.append(('field.submission_data', f))

        logging.info("System ID: %s", report.info['system_id'])
        logging.info("Submission ID: %s", report.info['submission_key'])

        if logging.getLogger().getEffectiveLevel() <= logging.DEBUG:
            logging.debug("Uncompressed payload length: %d", len(payload))

        start_time = time.time()

        ret = self._transport.exchange(form)

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
                     len(form), len(response),
                     format_delta(time.time() - start_time))


factory = LaunchpadReport
