import os

from hwtest.plugin import Plugin
from hwtest.report_helpers import createElement, createTypedElement
from hwtest.lib.conversion import string_to_int


class Processor(object):

    def __init__(self, **kwargs):
        self.properties = kwargs


class ProcessorManager(object):

    default_filename = os.path.join(os.sep, 'proc', 'cpuinfo')

    def __init__(self, filename=None):
        self._filename = filename or self.default_filename

    def get_processors(self):
        processors = []
        cpuinfo = {}
        fd = file(self._filename, "r")

        for line in map(lambda l: l.strip(), fd.readlines()):
            if not line:
                processor = Processor(**cpuinfo)
                processors.append(processor)
                cpuinfo = {}
            elif line.find(":") != -1:
                (key, value) = line.split(':', 1)
                key = key.strip()
                key = key.replace(' ', '_')
                key = key.lower()
                value = value.strip()
                if key == 'flags':
                    value = value.split()
                else:
                    value = string_to_int(value)
                cpuinfo[key] = value

        return processors

class ProcessorInfo(Plugin):
    
    def __init__(self, processor_manager=None):
        self._processors = []
        self._processor_manager = processor_manager or ProcessorManager()

    def register(self, manager):
        self._manager = manager
        self._persist = self._manager.persist.root_at('processor_info')
        self._manager.reactor.call_on('gather_information', self.gather_information)
        self._manager.reactor.call_on('run', self.run)

    def gather_information(self):
        report = self._manager.report
        if not report.finalised:
            content = self._processors

            processors = createElement(report, 'processors', report.root)
            for processor in self._processors:
                createTypedElement(report, 'processor', processors,
                str(self._processors.index(processor)), processor.properties,
                               True)

    def run(self):
        self._processors = self._processor_manager.get_processors()

factory = ProcessorInfo
