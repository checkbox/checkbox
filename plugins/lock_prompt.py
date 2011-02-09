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
import fcntl
import posixpath
import signal

from time import time

from gettext import gettext as _

from checkbox.contrib.glock import GlobalLock, LockAlreadyAcquired

from checkbox.lib.safe import safe_make_directory

from checkbox.properties import Int, Path
from checkbox.plugin import Plugin


class LockPrompt(Plugin):

    # Filename where the application lock is stored.
    filename = Path(default="%(checkbox_data)s/lock")

    # Timeout after which to show an error prompt.
    timeout = Int(default=0)

    def register(self, manager):
        super(LockPrompt, self).register(manager)

        self._lock = None

        self._manager.reactor.call_on(
            "prompt-begin", self.prompt_begin, -1000)

    def prompt_begin(self, interface):
        directory = posixpath.dirname(self.filename)
        safe_make_directory(directory)

        # Try to lock the process
        self._lock = GlobalLock(self.filename)
        try:
            self._lock.acquire()
        except LockAlreadyAcquired:
            if time() - os.stat(self.filename).st_atime > self.timeout:
                self._manager.reactor.fire("prompt-error", interface,
                    _("There is another checkbox running. Please close it first."))
            self._manager.reactor.stop_all()

        # Stop the process if the lock is deleted
        def handler(signum, frame):
            self._manager.reactor.stop_all()

        signal.signal(signal.SIGIO, handler)
        fd = os.open(directory,  os.O_RDONLY)

        fcntl.fcntl(fd, fcntl.F_SETSIG, 0)
        fcntl.fcntl(fd, fcntl.F_NOTIFY, fcntl.DN_DELETE)


factory = LockPrompt
