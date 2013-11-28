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
from gettext import gettext as _


signal_description_table = {
    "SIGHUP":  _("Hangup detected on controlling terminal or death of controlling process"),
    "SIGINT":  _("Interrupt from keyboard"),
    "SIGQUIT": _("Quit from keyboard"),
    "SIGILL":  _("Illegal Instruction"),
    "SIGABRT": _("Abort signal from abort(3)"),
    "SIGFPE":  _("Floating point exception"),
    "SIGKILL": _("Kill signal"),
    "SIGSEGV": _("Invalid memory reference"),
    "SIGPIPE": _("Broken pipe: write to pipe with no readers"),
    "SIGALRM": _("Timer signal from alarm(2)"),
    "SIGTERM": _("Termination signal"),
    "SIGUSR1": _("User-defined signal 1"),
    "SIGUSR2": _("User-defined signal 2"),
    "SIGCHLD": _("Child stopped or terminated"),
    "SIGCONT": _("Continue if stopped"),
    "SIGSTOP": _("Stop process"),
    "SIGTSTP": _("Stop typed at tty"),
    "SIGTTIN": _("tty input for background process"),
    "SIGTTOU": _("tty output for background process")}

signal_name_table = {
    1: "SIGHUP",
    2: "SIGINT",
    3: "SIGQUIT",
    4: "SIGILL",
    6: "SIGABRT",
    8: "SIGFPE",
    9: "SIGKILL",
    10: "SIGUSR1",
    11: "SIGSEGV",
    12: "SIGUSR2",
    13: "SIGPIPE",
    14: "SIGALRM",
    15: "SIGTERM",
    16: "SIGUSR1",
    21: "SIGTTIN",
    22: "SIGTTOU",
    23: "SIGSTOP",
    24: "SIGTSTP",
    25: "SIGCONT",
    26: "SIGTTIN",
    27: "SIGTTOU",
    30: "SIGUSR1",
    31: "SIGUSR2"}

def signal_to_name(signal):
    """Convert a signal number to its string representation.

    Keyword arguments:
    signal -- number of the signal as returned by wait
    """

    if signal in signal_name_table:
        return signal_name_table[signal]
    return _("UNKNOWN")

def signal_to_description(signal):
    """Convert a signal number to its corresponding description.

    Keyword arguments:
    signal -- number of the signal as returned by wait
    """

    name = signal_to_name(signal)
    if name in signal_description_table:
        return signal_description_table[name]
    return _("Unknown signal")
