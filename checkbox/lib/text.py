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
def indent(text, count=1, step=2):
    """Intend each line of text by a given step.

    Keyword arguments:
    text -- text containing lines to indent
    count -- number of steps to indent (default 1)
    step -- number of spaces per indent (default 2)
    """

    indent = ' ' * step
    return "\n".join([indent * count + t for t in text.split("\n")])

def wrap(text, limit=72):
    """Wrap text into lines up to limit characters excluding newline.

    Keyword arguments:
    text -- text to wrap
    limit -- maximum number of characters per line (default 72)
    """

    lines = ['']
    if text:
        current = -1
        inside = False
        for line in text.split("\n"):
            words = line.split()
            if words:
                inside = True
                for word in words:
                    increment = len(word) + 1
                    if current + increment > limit:
                        current = -1
                        lines.append('')
                    current += increment
                    lines[-1] += word + ' '
            else:
                if inside:
                    inside = False
                    lines.append('')
                lines.append('')
                current = -1

    return "\n".join(lines)

def unwrap(text):
    lines = text.split("\n")
    lines = [l.strip() for l in lines]
    return " ".join(lines)
