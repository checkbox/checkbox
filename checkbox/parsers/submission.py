#
# This file is part of Checkbox.
#
# Copyright 2011 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Checkbox is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Checkbox.  If not, see <http://www.gnu.org/licenses/>.
#
import re

import logging

from datetime import (
    datetime,
    timedelta,
    )
from dateutil import tz

from checkbox.parsers.device import DeviceResult
from checkbox.parsers.udev import UdevParser
from checkbox.parsers.utils import implement_from_dict

try:
    import xml.etree.cElementTree as etree
except ImportError:
    import cElementTree as etree


_time_regex = re.compile(r"""
    ^(?P<year>\d\d\d\d)-(?P<month>\d\d)-(?P<day>\d\d)
    T(?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)
    (?:\.(?P<second_fraction>\d{0,6}))?
    (?P<tz>
        (?:(?P<tz_sign>[-+])(?P<tz_hour>\d\d):(?P<tz_minute>\d\d))
        | Z)?$
    """,
    re.VERBOSE)

_xml_illegal_regex = re.compile(
    u"([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])"
    + u"|([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])" % (
    unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
    unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),
    unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff)))


class HALDevice(object):

    def __init__(self, id, udi, properties):
        self.id = id
        self.udi = udi
        self.properties = properties


class SubmissionStream(object):

    default_size = 4096

    def __init__(self, stream):
        self.stream = stream
        self._buffer = ""
        self._buffers = []

    def read(self, size=None):
        if size is None:
            size = self.default_size

        info_start_regex = re.compile("^<info .*>$")
        info_end_regex = re.compile("^</info>$")

        in_info = False
        length = sum(len(buffer) for buffer in self._buffers)

        while length < size:
            try:
                buffer = self.stream.next()
            except StopIteration:
                break

            if not in_info:
                if info_start_regex.match(buffer):
                    in_info = True
                    self._buffer += "".join(self._buffers)
                    self._buffers = [buffer]
                else:
                    length += len(buffer)
                    self._buffers.append(buffer)
            else:
                self._buffers.append(buffer)
                if info_end_regex.match(buffer):
                    in_info = False

                    buffer = "".join(self._buffers)
                    self._buffers = []

                    if not _xml_illegal_regex.search(buffer):
                        length += len(buffer)
                        self._buffer += buffer

        if self._buffers:
            self._buffer += "".join(self._buffers)
            self._buffers = []

        if not self._buffer:
            return None

        data = self._buffer[:size]
        self._buffers = [self._buffer[size:]]
        self._buffer = ""

        return data


class SubmissionParser(object):

    default_name = "unknown"

    def __init__(self, stream, name=None):
        self.stream = SubmissionStream(stream)
        self.name = name or self.default_name

    def _getClient(self, node):
        return "_".join([node.get('name'), node.get('version')])

    def _getProperty(self, node):
        """Parse a <property> node.

        :return: (name, (value, type)) of a property.
        """
        return (node.get('name'), self._getValueAttribute(node))

    def _getProperties(self, node):
        """Parse <property> sub-nodes of node.

        :return: A dictionary, where each key is the name of a property;
                 the values are the tuples (value, type) of a property.
        """
        properties = {}
        for child in node.getchildren():
            name, value = self._getProperty(child)
            if name in properties:
                raise ValueError(
                    '<property name="%s"> found more than once in <%s>'
                    % (name, node.tag))
            properties[name] = value

        return properties

    def _getValueAttribute(self, node):
        """Return (value, type) of a <property> or <value> node."""
        type_ = node.get('type')
        if type_ in ('dbus.Boolean', 'bool'):
            value = node.text.strip() == 'True'

        elif type_ in ('str', 'dbus.String', 'dbus.UTF8String'):
            value = node.text.strip()

        elif type_ in ('dbus.Byte', 'dbus.Int16', 'dbus.Int32', 'dbus.Int64',
                       'dbus.UInt16', 'dbus.UInt32', 'dbus.UInt64', 'int',
                       'long'):
            value = int(node.text.strip())

        elif type_ in ('dbus.Double', 'float'):
            value = float(node.text.strip())

        elif type_ in ('dbus.Array', 'list'):
            value = [self._getValueAttribute(child)
                for child in node.getchildren()]

        elif type_ in ('dbus.Dictionary', 'dict'):
            value = dict((child.get('name'), self._getValueAttribute(child))
                for child in node.getchildren())

        else:
            # This should not happen.
            raise AssertionError(
                'Unexpected <property> or <value> type: %s' % type_)

        return value

    def _getValueAttributeAsBoolean(self, node):
        """Return the value of the attribute "value" as a boolean."""
        return node.attrib['value'] == "True"

    def _getValueAttributeAsString(self, node):
        """Return the value of the attribute "value"."""
        return node.attrib['value']

    def _getValueAttributeAsDateTime(self, node):
        """Convert a "value" attribute into a datetime object."""
        time_text = node.get('value')

        # we cannot use time.strptime: this function accepts neither fractions
        # of a second nor a time zone given e.g. as '+02:30'.
        match = _time_regex.search(time_text)

        if match is None:
            raise ValueError(
                'Timestamp with unreasonable value: %s' % time_text)

        time_parts = match.groupdict()

        year = int(time_parts['year'])
        month = int(time_parts['month'])
        day = int(time_parts['day'])
        hour = int(time_parts['hour'])
        minute = int(time_parts['minute'])
        second = int(time_parts['second'])
        second_fraction = time_parts['second_fraction']
        if second_fraction is not None:
            milliseconds = second_fraction + '0' * (6 - len(second_fraction))
            milliseconds = int(milliseconds)
        else:
            milliseconds = 0

        if second > 59:
            second = 59
            milliseconds = 999999

        timestamp = datetime(year, month, day, hour, minute, second,
                             milliseconds, tzinfo=tz.tzutc())

        tz_sign = time_parts['tz_sign']
        tz_hour = time_parts['tz_hour']
        tz_minute = time_parts['tz_minute']
        if tz_sign in ('-', '+'):
            delta = timedelta(hours=int(tz_hour), minutes=int(tz_minute))
            if tz_sign == '-':
                timestamp = timestamp + delta
            else:
                timestamp = timestamp - delta

        return timestamp

    def _parseHAL(self, result, node):
        result.startDevices()
        for child in node.getchildren():
            id = int(child.get('id'))
            udi = child.get('udi')
            properties = self._getProperties(child)
            device = HALDevice(id, udi, properties)
            result.addDevice(device)

        result.endDevices()

    def _parseInfo(self, result, node):
        command = node.attrib['command']
        if command == "udevadm info --export-db":
            self._parseUdev(result, node)

        result.addInfo(command, node.text)

    def _parseUdev(self, result, node):
        result.startDevices()

        stream = StringIO(node.text)
        udev = UdevParser(stream)
        udev.run(result)

        result.endDevices()

    def _parseProcessors(self, result, node):
        result.startProcessors()

        for child in node.getchildren():
            id = int(child.get('id'))
            name = child.get('name')
            properties = self._getProperties(child)
            result.addProcessor(id, name, properties)

        result.endProcessors()

    def _parseRoot(self, result, node):
        parsers = {
            "summary": self._parseSummary,
            "hardware": self._parseHardware,
            "software": self._parseSoftware,
            "questions": self._parseQuestions,
            "context": self._parseContext,
            }

        for child in node.getchildren():
            parser = parsers.get(child.tag, self._parseNone)
            parser(result, child)

    def _parseSummary(self, result, node):
        parsers = {
            'live_cd': self._getValueAttributeAsBoolean,
            'system_id': self._getValueAttributeAsString,
            'distribution': self._getValueAttributeAsString,
            'distroseries': self._getValueAttributeAsString,
            'architecture': self._getValueAttributeAsString,
            'private': self._getValueAttributeAsBoolean,
            'contactable': self._getValueAttributeAsBoolean,
            'date_created': self._getValueAttributeAsDateTime,
            'client': self._getClient,
            'kernel-release': self._getValueAttributeAsString,
            }

        for child in node.getchildren():
            parser = parsers.get(child.tag, self._parseNone)
            value = parser(child)
            result.addSummary(child.tag, value)

    def _parseHardware(self, result, node):
        parsers = {
            'hal': self._parseHAL,
            'processors': self._parseProcessors,
            'udev': self._parseUdev,
            }

        for child in node.getchildren():
            parser = parsers.get(child.tag, self._parseNone)
            parser(result, child)

    def _parseLSBRelease(self, result, node):
        properties = self._getProperties(node)
        result.setDistribution(**properties)

    def _parsePackages(self, result, node):
        result.startPackages()

        for child in node.getchildren():
            id = int(child.get('id'))
            name = child.get('name')
            properties = self._getProperties(child)

            result.addPackage(id, name, properties)

        result.endPackages()

    def _parseXOrg(self, result, node):
        drivers = {}
        for child in node.getchildren():
            info = dict(child.attrib)
            if 'device' in info:
                info['device'] = int(info['device'])

            name = info['name']
            if name in drivers:
                raise ValueError(
                    '<driver name="%s"> appears more than once in <xorg>'
                    % name)

            drivers[name] = info

        version = node.get('version')
        result.addXorg(version, drivers)

    def _parseSoftware(self, result, node):
        parsers = {
            'lsbrelease': self._parseLSBRelease,
            'packages': self._parsePackages,
            'xorg': self._parseXOrg,
            }

        for child in node.getchildren():
            parser = parsers.get(child.tag, self._parseNone)
            parser(result, child)

    def _parseQuestions(self, result, node):
        result.startQuestions()

        for child in node.getchildren():
            question = {'name': child.get('name')}
            plugin = child.get('plugin', None)
            if plugin is not None:
                question['plugin'] = plugin
            question['targets'] = targets = []
            answer_choices = []

            for sub_node in child.getchildren():
                sub_tag = sub_node.tag
                if sub_tag == 'answer':
                    question['answer'] = answer = {}
                    answer['type'] = sub_node.get('type')
                    if answer['type'] == 'multiple_choice':
                        question['answer_choices'] = answer_choices
                    unit = sub_node.get('unit', None)
                    if unit is not None:
                        answer['unit'] = unit
                    answer['value'] = sub_node.text.strip()
                elif sub_tag == 'answer_choices':
                    for value_node in sub_node.getchildren():
                        answer_choices.append(
                            self._getValueAttribute(value_node))
                elif sub_tag == 'target':
                    target = {'id': int(sub_node.get('id'))}
                    target['drivers'] = drivers = []
                    for driver_node in sub_node.getchildren():
                        drivers.append(driver_node.text.strip())
                    targets.append(target)
                elif sub_tag in('comment', 'command'):
                    data = sub_node.text
                    if data is not None:
                        question[sub_tag] = data.strip()

            result.addQuestion(question)

        result.endQuestions()

    def _parseContext(self, result, node):
        parsers = {
            'info': self._parseInfo,
            }

        for child in node.getchildren():
            parser = parsers.get(child.tag, self._parseNone)
            parser(result, child)

    def _parseNone(self, result, node):
        pass

    def run(self, result):
        parser = etree.XMLParser()

        try:
            tree = etree.parse(self.stream, parser=parser)
        except SyntaxError, error:
            logging.error(error)
            return

        root = tree.getroot()
        if root.tag != "system":
            logging.error("Root node is not '<system>'")
            return

        self._parseRoot(result, root)


SubmissionResult = implement_from_dict("SubmissionResult", [
    "startDevices", "endDevices", "addDevice", "startPackages",
    "endPackages", "addPackage", "startProcessors", "endProcessors",
    "addProcessor", "startQuestions", "endQuestions", "addQuestion",
    "addInfo", "addSummary", "addXorg", "setDistribution"], DeviceResult)
