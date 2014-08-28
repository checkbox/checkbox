# Copyright (C) 2014 Canonical Ltd.
#
# Authors
#   Daniel Manrique <daniel.manrique@canonical.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
A bzr plugin to output log information in a custom format for checkbox
release notes.
1- Drop this in  ~/.bazaar/plugins/
2- add -v --log-format 'cb' OR --cb to your usual bzr log line (i.e. the one
you'd use to select the portions of the log you wish to report)


What does it do?
===============

* Selection of which commits to report is up to the user, use standard
  bzr log commit selection (e.g. -r something..something, --match-*)

* Signed-off-by: portions will be stripped from messages.

* Messages containing "automatic merge by tarmac" will be ignored.

* Messages will be grouped by author name (minus the email address)

* This will be output to stdout
"""

import collections
import re
import textwrap

import bzrlib.log


class CbFormatter(bzrlib.log.LogFormatter):

    def __init__(self, *args, **kwargs):
        bzrlib.log.LogFormatter.__init__(self, *args, **kwargs)
        self._date_line = None
        self.supports_tags = True
        self.supports_delta = True
        self.supports_merge_revisions = True

    def log_revision(self, lr):
        if not "automatic merge by tarmac" in lr.rev.message:
            message = lr.rev.message
            message = re.sub(r'Signed-off-by: .+ <.+>','', message)
            self.my_revisions.append(message)
            for author in lr.rev.get_apparent_authors():
                self.my_authors.add(author)
                self.author_rev_map[author].append(message)

    def begin_log(self):
        self.my_revisions = list()
        self.my_authors = set()
        self.author_rev_map = collections.defaultdict(list)

    def end_log(self):
        for author in self.my_authors:
            print("  [ %s ]" % re.sub(r'<.+>', '', author).strip())
            for rev in self.author_rev_map[author]:
                change_text = rev.splitlines()
                change_text = [line.lstrip("*").strip() for line in change_text]
                change_text = " ".join(change_text)
                change_text = re.sub(r' +',' ', change_text)
                wrapper = textwrap.TextWrapper(initial_indent="  * ",
                                               subsequent_indent=" " * 4,
                                               width=70,
                                               replace_whitespace=True)
                change_text = change_text.replace("#changelog","")
                change_text = wrapper.fill(change_text)
                print(change_text.encode('UTF-8'))
            print("")


bzrlib.log.register_formatter('cb', CbFormatter)
