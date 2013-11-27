#
# This file is part of Checkbox.
#
# Copyright 2008 Canonical Ltd.
#
# Checkbox is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.

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
import logging
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
    logger = logging.getLogger()

    def register(self, manager):
        super(LockPrompt, self).register(manager)

        self._lock = None
        self._fd = None

        self._manager.reactor.call_on(
            "prompt-begin", self.prompt_begin, -1000)
        self._manager.reactor.call_on("stop", self.release, 1000)

    def prompt_begin(self, interface):
        directory = posixpath.dirname(self.filename)
        safe_make_directory(directory)

        # Try to lock the process
        self._lock = GlobalLock(self.filename, logger=self.logger)
        try:
            self._lock.acquire()
        except LockAlreadyAcquired:
            if time() - os.stat(self.filename).st_atime > self.timeout:
                self._manager.reactor.fire("prompt-error", interface,
                    _("There is another checkbox running. Please close it first."))
            self._manager.reactor.stop_all()

        # Stop the process if the lock is deleted
        def handler(signum, frame):
            if not posixpath.exists(self.filename):
                self._manager.reactor.stop_all()
        
        signal.signal(signal.SIGIO, handler)
        self._fd = os.open(directory,  os.O_RDONLY)

        fcntl.fcntl(self._fd, fcntl.F_SETSIG, 0)
        fcntl.fcntl(self._fd, fcntl.F_NOTIFY, fcntl.DN_DELETE|fcntl.DN_MULTISHOT)

    def release(self):
        # Properly release to the lock
        self._lock.release(skip_delete=True)
        os.close(self._fd)
        os.unlink(self.filename)

factory = LockPrompt
