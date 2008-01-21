import os
import re
import logging


class Template(object):

    def __init__(self, validator=lambda t, e: True):
        self._validator = validator

        self.filename = None
        self.elements = []

    def _reader(self, fd, size=4096, delimiter="\n\n"):
        buffer = ''
        while True:
            lines = (buffer + fd.read(size)).split(delimiter)
            buffer = lines.pop(-1)
            if not lines:
                break
            for line in lines:
                yield line

        yield buffer

    def load_filename(self, filename):
        logging.info("Loading elements from filename: %s", filename)

        self.filename = filename

        elements = []
        descriptor = file(filename, "r")
        for string in self._reader(descriptor):
            if not string:
                break

            element = {}

            def _save(field, value, extended):
                if value and extended:
                    raise Exception, \
                        "Path %s has both a value and an extended value." \
                            % filename
                extended = extended.rstrip("\n")
                if field:
                    if element.has_key(field):
                        raise Exception, \
                            "Path %s has a duplicate field '%s'" \
                            " with a new value '%s'." \
                                % (filename, field, value)
                    element[field] = value or extended

            string = string.strip("\n")
            field = value = extended = ''
            for line in string.split("\n"):
                line.strip()
                match = re.search(r"^([-_.A-Za-z0-9]*):\s?(.*)", line)
                if match:
                    _save(field, value, extended)
                    field = match.groups()[0].lower()
                    value = match.groups()[1].rstrip()
                    extended = ''
                    basefield = re.sub(r"-.+$", "", field)
                    continue

                if re.search(r"^\s\.$", line):
                    extended += "\n\n"
                    continue

                match = re.search(r"^\s(\s+.*)", line)
                if match:
                    bit = match.groups()[0].rstrip()
                    if len(extended) and not re.search(r"[\n ]$", extended):
                        extended += "\n"

                    extended += bit + "\n"
                    continue

                match = re.search(r"^\s(.*)", line)
                if match:
                    bit = match.groups()[0].rstrip()
                    if len(extended) and not re.search(r"[\n ]$", extended):
                        extended += " "

                    extended += bit
                    continue

                raise Exception, "Path %s parse error at: %s" \
                    % (filename, line)

            _save(field, value, extended)

            self._validator(self, element)

            elements.append(element)

        return elements

    def load_directory(self, directory, blacklist=[]):
        logging.info("Loading elements from directory: %s", directory)

        elements = []
        for name in os.listdir(directory):
            if name not in blacklist:
                filename = os.path.join(directory, name)
                elements.extend(self.load_filename(filename))

        return elements

    def load_directories(self, directories, blacklist=[]):
        elements = []
        for directory in directories:
            elements.extend(self.load_directory(directory, blacklist))

        return elements
