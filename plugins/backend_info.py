#
# This file is part of Checkbox.
#
# Copyright 2010 Canonical Ltd.
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
import shutil
import logging

from subprocess import call, PIPE
from tempfile import mkdtemp

from checkbox.lib.fifo import FifoReader, FifoWriter, create_fifo

from checkbox.plugin import Plugin
from checkbox.properties import Path, Float
from checkbox.job import FAIL

from gettext import gettext as _


class BackendInfo(Plugin):

    # how long to wait for I/O from/to the backend before the call returns.
    # How we behave if I/O times out is dependent on the situation.
    timeout = Float(default=60.0)

    command = Path(default="%(checkbox_share)s/backend")

    next_sequence = 0
    expected_sequence = 0

    def write_to_parent(self, object):
        message = (self.next_sequence, object,)
        logging.debug("Sending message with sequence number %s to backend" %
                       self.next_sequence)
        self.parent_writer.write_object(message)
        self.expected_sequence = self.next_sequence
        self.next_sequence += 1

    def read_from_parent(self):
        correct_sequence = False
        while not correct_sequence:
            ro = self.parent_reader.read_object()
            if ro:
                sequence, result = ro
                logging.debug("Expecting sequence number %s from backend, "
                              "got sequence number %s" %
                       (self.expected_sequence, sequence))
                if (self.expected_sequence == sequence):
                    correct_sequence = True
                else:
                    logging.warning("Backend sent wrong sequence number, "
                                    "Discarding message and re-reading")
            else:
                #If we timed out, just return nothing, the rest of
                #the code knows how to handle this.
                return ro
        return result

    def register(self, manager):
        super(BackendInfo, self).register(manager)

        for (rt, rh) in [
             ("message-exec", self.message_exec),
             ("stop", self.stop)]:
            self._manager.reactor.call_on(rt, rh)

        # Backend should run as early as possible
        self._manager.reactor.call_on("gather", self.gather, -100)

    def get_command(self, *args):
        command = [self.command, "--path=%s" % os.environ["PATH"]]

        return command + list(args)

    def get_root_command(self, *args):
        uid = os.getuid()
        password_text = _("SYSTEM TESTING: Please enter your password. "
                          "Some tests require root access to run properly. "
                          "Your password will never be stored and will never "
                          "be submitted with test results.")
        password_prompt = _("PASSWORD: ")
        if uid == 0:
            prefix = []
        elif os.getenv("DISPLAY") and \
                call(["which", "kdesudo"],
                    stdout=PIPE, stderr=PIPE) == 0 and \
                call(["pgrep", "-x", "-u", str(uid), "ksmserver"],
                    stdout=PIPE, stderr=PIPE) == 0:
            prefix = ["kdesudo", "--comment", password_text, "-d", "--"]
        elif os.getenv("DISPLAY") and \
                call(["which", "gksu"],
                    stdout=PIPE, stderr=PIPE) == 0 and \
                call(["pgrep", "-x", "-u", str(uid), "gnome-panel|gconfd-2"],
                    stdout=PIPE, stderr=PIPE) == 0:
            prefix = ["gksu", "--message", password_text, "--"]
        else:
            prefix = ["sudo", "-p", password_text + " " + password_prompt]

        return prefix + self.get_command(*args)

    def spawn_backend(self, input_fifo, output_fifo):
        self.pid = os.fork()
        if self.pid == 0:
            root_command = self.get_root_command(input_fifo, output_fifo)
            os.execvp(root_command[0], root_command)
            # Should never get here

    def ping_backend(self):
        if not self.parent_reader or not self.parent_writer:
            return False
        self.write_to_parent("ping")
        result = self.read_from_parent()
        return result == "pong"

    def gather(self):
        self.directory = mkdtemp(prefix="checkbox")
        child_input = create_fifo(os.path.join(self.directory, "input"),
                                  0o600)
        child_output = create_fifo(os.path.join(self.directory, "output"),
                                   0o600)

        self.backend_is_alive = False
        for attempt in range(1, 4):
            self.spawn_backend(child_input, child_output)
            #Only returns if I'm still the parent,
            #so I can do parent stuff here
            self.parent_writer = FifoWriter(child_input, timeout=self.timeout)
            self.parent_reader = FifoReader(child_output,
                                            timeout=self.timeout)
            if self.ping_backend():
                logging.debug("Backend responded, continuing execution.")
                self.backend_is_alive = True
                break
            else:
                logging.debug("Backend didn't respond, "
                              "trying to create again.")

        if not self.backend_is_alive:
            logging.warning("Privileged backend not responding. " +
                            "jobs specifying user will not be run")

    def message_exec(self, message):
        if "user" in message:
            if "environ" in message:
                #Prepare variables to be "exported" from my environment
                #to the backend's.
                backend_environ = ["%s=%s" % (key, os.environ[key])
                             for key in message["environ"]
                             if key in os.environ]
                message = dict(message)  # so as to not wreck the
                                         # original message
                message["environ"] = backend_environ

            if (self.backend_is_alive and not self.ping_backend()):
                self.backend_is_alive = False

            if self.backend_is_alive:
                self.write_to_parent(message)
                while True:
                    result = self.read_from_parent()
                    if result:
                        break
                    else:
                        logging.info("Waiting for result...")
            else:
                result = (FAIL, "Unable to test. Privileges are " +
                                "required for this job.", 0,)
            if result:
                self._manager.reactor.fire("message-result", *result)

    def stop(self):
        self.write_to_parent("stop")
        self.parent_writer.close()
        self.parent_reader.close()
        shutil.rmtree(self.directory)

        if self.backend_is_alive:
            os.waitpid(self.pid, 0)


factory = BackendInfo
