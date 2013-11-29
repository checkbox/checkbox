#
# This file is part of Checkbox.
#
# Copyright 2011 Canonical Ltd.
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
import re

from checkbox.lib.enum import Enum


DescriptionState = Enum(
    "INIT",
    "PURPOSE",
    "STEPS",
    "INFO",
    "VERIFICATION",
    "OTHER")

TransitionStates = {
    DescriptionState.INIT: DescriptionState.PURPOSE,
    DescriptionState.PURPOSE: DescriptionState.STEPS,
    DescriptionState.STEPS: DescriptionState.VERIFICATION,
    DescriptionState.INFO: DescriptionState.VERIFICATION,
    DescriptionState.VERIFICATION: DescriptionState.OTHER,
    DescriptionState.OTHER: DescriptionState.OTHER,
    }

# PURPOSE string:
#   1. Foo
# substitute to:
#   Foo
PURPOSE_RE = re.compile(r"(\d+)\.(\s+)", re.M)

# STEPS string:
#   1: Foo
# substitute to:
#   1. Foo
STEPS_RE = re.compile(r"(\d+):(\s+)", re.M)


class DescriptionParser:
    """Parser for the description field in jobs."""

    def __init__(self, stream):
        self.stream = stream

    def run(self, result):
        parts = {}
        state = DescriptionState.INIT

        for line in self.stream.readlines():
            # Check for upper case characters without leading spaces.
            if not line[0].isspace() \
               and line.isupper():
                state = TransitionStates[state]

            # Append to description parts between INIT and OTHER states.
            elif state > DescriptionState.INIT \
                 and state < DescriptionState.OTHER:
                # Handle optional INFO state and translations of $output.
                if state == DescriptionState.VERIFICATION \
                   and "$" in line:
                    state = DescriptionState.INFO
                    line = "$output\n"

                parts.setdefault(state, "")
                parts[state] += line.lstrip()

        # Only set the description if the last state is still VERIFICATION.
        if state == DescriptionState.VERIFICATION:
            # Substitute the PURPOSE part
            parts[DescriptionState.PURPOSE] = PURPOSE_RE.sub(
                r"", parts[DescriptionState.PURPOSE])

            # Substitute the STEPS part
            parts[DescriptionState.STEPS] = STEPS_RE.sub(
                r"\1.\2", parts[DescriptionState.STEPS])

            result.setDescription(
                parts[DescriptionState.PURPOSE],
                parts[DescriptionState.STEPS],
                parts[DescriptionState.VERIFICATION],
                parts.get(DescriptionState.INFO))
