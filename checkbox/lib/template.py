#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
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
import os
import re
import logging
import posixpath


class Template(object):

    def __init__(self, filename_field=None, unique_fields=[]):
        self._filename_field = filename_field
        self._unique_fields = unique_fields

    def _reader(self, file, size=4096, delimiter="\n\n"):
        buffer_old = ""
        while True:
            buffer_new = file.read(size)
            if not buffer_new:
                break

            lines = (buffer_old + buffer_new).split(delimiter)
            buffer_old = lines.pop(-1)

            for line in lines:
                yield line

        yield buffer_old

    def load_file(self, file, filename="<stream>"):
        elements = []
        for string in self._reader(file):
            if not string:
                break

            element = {}

            def _save(field, value, extended):
                extended = extended.rstrip("\n")
                if field:
                    if element.has_key(field):
                        raise Exception, \
                            "Template %s has a duplicate field '%s'" \
                            " with a new value '%s'." \
                                % (filename, field, value)
                    element[field] = value
                    if extended:
                        element["%s_extended" % field] = extended

            string = string.strip("\n")
            field = value = extended = ""
            for line in string.split("\n"):
                line.strip()
                match = re.search(r"^([-_.A-Za-z0-9]*):\s?(.*)", line)
                if match:
                    _save(field, value, extended)
                    field = match.groups()[0].lower()
                    value = match.groups()[1].rstrip()
                    extended = ""
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

                raise Exception, "Template %s parse error at: %s" \
                    % (filename, line)

            _save(field, value, extended)

            # Sanity checks
            if self._filename_field:
                if self._filename_field in element:
                    raise Exception, \
                        "Template %s already contains filename field: %s" \
                        % (filename, self._filename_field)
                element[self._filename_field] = posixpath.basename(filename)

            for unique_field in self._unique_fields:
                if [e for e in elements \
                   if e[unique_field] == element[unique_field]]:
                    raise Exception, \
                        "Template %s contains duplicate fields: %s" \
                        % (filename, unique_field)

            elements.append(element)

        return elements

    def load_filename(self, filename):
        logging.info("Loading elements from filename: %s", filename)

        file = open(filename, "r")
        return self.load_file(file, filename)

    def load_directory(self, directory, blacklist=[], whitelist=[]):
        logging.info("Loading filenames from directory: %s", directory)

        whitelist_patterns = [re.compile(r"^%s$" % r) for r in whitelist]
        blacklist_patterns = [re.compile(r"^%s$" % r) for r in blacklist]

        elements = []
        for name in os.listdir(directory):
            if name.startswith(".") or name.endswith("~"):
                logging.info("Ignored filename: %s", name)
                continue

            if whitelist_patterns:
                if not [name for p in whitelist_patterns if p.match(name)]:
                    logging.info("Not whitelisted filename: %s", name)
                    continue
            elif blacklist_patterns:
                if [name for p in blacklist_patterns if p.match(name)]:
                    logging.info("Blacklisted filename: %s", name)
                    continue

            filename = posixpath.join(directory, name)
            elements.extend(self.load_filename(filename))

        return elements

    def load_directories(self, directories, blacklist=[], whitelist=[]):
        elements = []
        for directory in directories:
            elements.extend(self.load_directory(directory, blacklist, whitelist))

        return elements
