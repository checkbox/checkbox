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
import time
import fcntl
import select
import signal


STDIN_FILENO = 0
STDOUT_FILENO = 1
STDERR_FILENO = 2

DEFAULT_OPEN_MAX = 1024


class Process:
    """Class representing a child process which is non blocking. This makes
       it possible to return within a specified timeout."""

    def __init__(self, cmd, env={}, bufsize=8192):
        """The parameter 'cmd' is the shell command to execute in a
        sub-process. If the 'bufsize' parameter is specified, it
        specifies the size of the I/O buffers from the child process."""
        self.cleaned=False
        self.BUFSIZ=bufsize
        self.outr, self.outw = os.pipe()
        self.errr, self.errw = os.pipe()
        self.pid = os.fork()
        if self.pid == 0:
            self._child(cmd, env)
        os.close(self.outw) #parent doesn't write so close
        os.close(self.errw)
        # Note we could use self.stdout=fdopen(self.outr) here
        # to get a higher level file object like popen2.Popen3 uses.
        # This would have the advantages of auto handling the BUFSIZ
        # and closing the files when deleted. However it would mean
        # that it would block waiting for a full BUFSIZ unless we explicitly
        # set the files non blocking, and there would be extra uneeded
        # overhead like EOL conversion. So I think it's handier to use os.read()
        self.outdata = self.errdata = b""
        self.starttime = self.endtime = None
        self._outeof = self._erreof = False

    def _child(self, cmd, env):
        # Force FD_CLOEXEC on all inherited descriptors
        try:
            open_max = os.sysconf('SC_OPEN_MAX')
        except (AttributeError, ValueError):
            open_max = DEFAULT_OPEN_MAX
        for fileno in range(STDERR_FILENO+1, open_max):
            try:
                flags = fcntl.fcntl(fileno, fcntl.F_GETFD)
            except IOError:
                continue
            flags |= fcntl.FD_CLOEXEC
            fcntl.fcntl(fileno, fcntl.F_SETFD, flags)
        # stdout and stderr to write side of pipe
        os.dup2(self.outw, STDOUT_FILENO)
        os.dup2(self.errw, STDERR_FILENO)
        # stdout and stderr connected to pipe, so close all other files
        for fileno in self.outr, self.outw, self.errr, self.errw:
            os.close(fileno)
        try:
            cmd = ["/bin/bash", "-c", cmd]
            os.execve(cmd[0], cmd, env)
        finally: #exit child on error
            os._exit(1)

    def read(self, timeout=None):
        """return False when finished
           else return True every timeout seconds
           data will be in outdata and errdata"""
        has_finished = True
        self.starttime = time.time()
        while True:
            tocheck=[]
            if not self._outeof:
                tocheck.append(self.outr)
            if not self._erreof:
                tocheck.append(self.errr)
            ready = select.select(tocheck, [], [], timeout)
            if not len(ready[0]): # no data timeout
                has_finished = False
                break
            else:
                if self.outr in ready[0]:
                    outchunk = os.read(self.outr, self.BUFSIZ)
                    if outchunk == b"":
                        self._outeof = True
                    self.outdata += outchunk
                if self.errr in ready[0]:
                    errchunk = os.read(self.errr, self.BUFSIZ)
                    if errchunk == b"":
                        self._erreof = True
                    self.errdata += errchunk
                if self._outeof and self._erreof:
                    break
                elif timeout:
                    if (time.time() - self.starttime) > timeout:
                        has_finished = False
                        break # may be more data but time to go

        self.endtime = time.time()
        return has_finished

    def kill(self):
        os.kill(self.pid, signal.SIGTERM)

    def cleanup(self):
        """Wait for and return the exit status of the child process."""
        self.cleaned = True
        os.close(self.outr)
        os.close(self.errr)
        pid, status = os.waitpid(self.pid, 0)
        if pid == self.pid:
            self.status = status
        return self.status

    def __del__(self):
        if not self.cleaned:
            self.cleanup()
