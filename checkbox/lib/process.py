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
import select


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
        self.outdata = self.errdata = ""
        self.starttime = self.endtime = None
        self._outeof = self._erreof = 0

    def _child(self, cmd, env):
        # Note sh below doesn't setup a seperate group (job control)
        # for non interactive shells (hmm maybe -m option does?)
        os.setpgrp() #seperate group so we can kill it
        os.dup2(self.outw,1) #stdout to write side of pipe
        os.dup2(self.errw,2) #stderr to write side of pipe
        #stdout & stderr connected to pipe, so close all other files
        map(os.close, [self.outr,self.outw,self.errr,self.errw])
        try:
            cmd = ["/bin/sh", "-c", cmd]
            os.execve(cmd[0], cmd, env)
        finally: #exit child on error
            os._exit(1)

    def read(self, timeout=None):
        """return 0 when finished
           else return 1 every timeout seconds
           data will be in outdata and errdata"""
        self.starttime = time.time()
        while 1:
            tocheck=[]
            if not self._outeof:
                tocheck.append(self.outr)
            if not self._erreof:
                tocheck.append(self.errr)
            ready = select.select(tocheck, [], [], timeout)
            if len(ready[0]) == 0: #no data timeout
                return 1
            else:
                if self.outr in ready[0]:
                    outchunk = os.read(self.outr, self.BUFSIZ)
                    if outchunk == "":
                        self._outeof = 1
                    self.outdata += outchunk
                if self.errr in ready[0]:
                    errchunk = os.read(self.errr, self.BUFSIZ)
                    if errchunk == "":
                        self._erreof = 1
                    self.errdata += errchunk
                if self._outeof and self._erreof:
                    self.endtime = time.time()
                    return 0
                elif timeout:
                    if (time.time() - self.starttime) > timeout:
                        return 1 # may be more data but time to go

    def kill(self):
        os.kill(-self.pid, 15) # SIGTERM whole group

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
