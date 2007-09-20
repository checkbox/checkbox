#! /usr/bin/python

import md5
import zlib

from datetime import datetime
from xml.dom.minidom import Document

from hwtest.report_helpers import createElement, createTypedElement

class ReportInfo(dict):
    """Simple class to contain report summary information."""

    def __init__(self):
        self['format'] = 'VERSION_1'
        self['private'] = False
        self['contactable'] = False
        self['livecd'] = False

class Report(object):
    def __init__(self):
        self.info = ReportInfo()
        self.xml = Document()
        self.root = createElement(self, 'system', self.xml)
        self.root.setAttribute('version', '1.0')
        self.summary = createElement(self, 'summary', self.root)
        self._finalised = False

    def finalise(self):
        if not self._finalised:
            self.info['date_created'] = datetime.utcnow()

            for child in self.summary.childNodes:
                self.summary.removeChild(child)

            for key in self.info.keys():
                createElement(self, key, self.summary, self.info[key])

            self._finalised = True

        submission = md5.new()
        submission.update(self.info['system'])
        submission.update(str(datetime.utcnow()))
        self.info['submission_id'] = submission.hexdigest()

    def toxml(self):
        self.finalise()
        return self.xml.toxml()

    def display(self):
        self.finalise()
        print self.xml.toprettyxml('')

    def save(self, filename='system.hwi', compress=False):
        #self.finalise()
        report_file = open(filename, 'w')
        if compress:
            contents = zlib.compress(self.xml.toxml(), 9)
        else:
            contents = self.xml.toxml()
        report_file.write(contents)
        report_file.close()
