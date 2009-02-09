#
# Copyright (c) 2008 Canonical
#
# Written by Marc Tardif <marc@interunion.ca>
#
# This file is part of Checkbox.
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
import re

from checkbox.lib.text import wrap as text_wrap
from checkbox.lib.text import unwrap as text_unwrap


def _apply_text_function(text, function, *args, **kwargs):
    paragraphs = re.split(r"\n{2,}", text)
    paragraphs = [function(p, *args, **kwargs) for p in paragraphs]
    return "\n\n".join(paragraphs)

def wrap(text, limit=72):
    return _apply_text_function(text, text_wrap, limit)

def unwrap(text):
    return _apply_text_function(text, text_unwrap)
