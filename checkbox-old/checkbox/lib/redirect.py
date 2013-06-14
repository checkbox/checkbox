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
import sys
import tempfile


def _file_write(file):
    # file is a filename, a pipe-command, a fileno(), or a file
    # returns file.
    if not hasattr(file, "write"):
        if file[0] == "|":
            file = os.popen(file[1:], "w")
        else:
            file = open(file, "w")

    return file

def _file_read(file):
    # file is a filename, a pipe-command, or a file
    # returns file.
    if not hasattr(file, "read"):
        if file[-1] == "|":
            file = os.popen(file[1:], "r")
        else:
            file = open(file, "r")

    return file

def redirect_to_file(file, func, *args):
    # apply func(args), temporarily redirecting stdout to file.
    # file can be a file or any writable object, or a filename string.
    # a "|cmd" string will pipe output to cmd.
    # Returns value of apply(func, *args)
    ret = None
    file = _file_write(file)
    sys.stdout, file = file, sys.stdout
    try:
        ret = func(*args)
    finally:
        print(ret)
        sys.stdout, file = file, sys.stdout
    return ret

def redirect_to_string(func, *args):
    # apply func(*args) with stdout redirected to return string.
    file = tempfile.TemporaryFile()
    redirect_to_file(*(file, func) + args)
    file.seek(0)
    return file.read()

def redirect_to_lines(func, *args):
    # apply func(*args), returning a list of redirected stdout lines.
    file = tempfile.TemporaryFile()
    redirect_to_file(*(file, func) + args)
    file.seek(0)
    return file.readlines()


class RedirectTee:

    def __init__(self, *optargs):
        self._files = []
        for arg in optargs:
            self.addfile(arg)

    def addfile(self, file):
        self._files.append(_file_write(file))

    def remfile(self, file):
        file.flush()
        self._files.remove(file)

    def files(self):
        return self._files

    def write(self, what):
        for eachfile in self._files:
            eachfile.write(what)

    def writelines(self, lines):
        for eachline in lines: self.write(eachline)

    def flush(self):
        for eachfile in self._files:
            eachfile.flush()

    def close(self):
        for eachfile in self._files:
            self.remfile(eachfile)  # Don't CLOSE the real files.

    def CLOSE(self):
        for eachfile in self._files:
            self.remfile(eachfile)
            self.eachfile.close()

    def isatty(self):
        return 0


class RedirectEcho:

    def __init__(self, input, *output):
        self._infile = _file_read(input)
        if output:
            self._output = _file_write(output[0])
        else:
            self._output = None

    def read(self, *howmuch):
        stuff = self._infile.read(*howmuch)
        if self._output:
            self._output.write(stuff)
        return stuff

    def readline(self):
        line = self._infile.readline()
        self._output.write(line)
        return line

    def readlines(self):
        out = []
        while True:
            out.append(self.readline())
            if not out[-1]:
                return out[:-1]

    def flush(self):
        self._output.flush()

    def seek(self, where, how):
        self._infile.seek(where, how)

    def tell(self):
        return self._infile.tell()

    def isatty(self):
        return self._infile.isatty()

    def close(self):
        self._infile.close()
        self._output.close()
