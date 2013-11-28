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
import logging
import itertools
import posixpath

from checkbox.contrib import bpickle
from checkbox.lib.safe import safe_close

HELD = "h"
BROKEN = "b"

ANCIENT = 1


class Message(dict):

    def __init__(self, message, filename):
        super(Message, self).__init__(message)
        self.filename = filename


class MessageStore:
    """A message store which stores its messages in a file system hierarchy."""

    # This caches everything but a message's data, making it manageable to keep
    # in memory.
    _message_cache = {}

    # Setting this to False speeds things up considerably, at the expense of a
    # higher risk of data loss during a crash
    safe_file_closing = True

    def __init__(self, persist, directory, directory_size=1000):
        self._directory = directory
        self._directory_size = directory_size
        self._original_persist = persist
        self._persist = persist.root_at("message-store")
        message_dir = self._message_dir()
        if not posixpath.isdir(message_dir):
            os.makedirs(message_dir)

    def commit(self):
        """Save metadata to disk."""
        self._original_persist.save()

    def get_sequence(self):
        """
        Get the sequence number of the message that the server expects us to
        send on the next exchange.
        """
        return self._persist.get("sequence", 0)

    def set_sequence(self, number):
        """
        Set the sequence number of the message that the server expects us to
        send on the next exchange.
        """
        self._persist.set("sequence", number)

    def get_pending_offset(self):
        return self._persist.get("pending_offset", 0)

    def set_pending_offset(self, val):
        """
        Set the offset into the message pool to consider assigned to the
        current sequence number as returned by l{get_sequence}.
        """
        self._persist.set("pending_offset", val)

    def add_pending_offset(self, val=1):
        self.set_pending_offset(self.get_pending_offset() + val)

    def remove_pending_offset(self, val=1):
        pending_offset = self.get_pending_offset()
        if pending_offset - val < 0:
            return False

        self.set_pending_offset(pending_offset - val)
        return True

    def count_pending_messages(self):
        """Return the number of pending messages."""
        return sum(1 for x in self._walk_pending_messages())

    def get_pending_messages(self, max=None):
        """Get any pending messages that aren't being held, up to max."""
        messages = []
        for filename in self._walk_pending_messages():
            if max is not None and len(messages) >= max:
                break
            try:
                message = self._read_message(filename)
            except ValueError as e:
                logging.exception(e)
                self._add_flags(filename, BROKEN)
            else:
                messages.append(message)

        return messages

    def set_pending_flags(self, flags):
        for filename in self._walk_pending_messages():
            self._set_flags(filename, flags)
            break

    def add_pending_flags(self, flags):
        for filename in self._walk_pending_messages():
            self._add_flags(filename, flags)
            break

    def delete_old_messages(self):
        """Delete messages which are unlikely to be needed in the future."""
        filenames = itertools.islice(
            self._walk_messages(exclude=HELD + BROKEN),
            self.get_pending_offset())
        for filename in filenames:
            os.unlink(filename)
            containing_dir = os.path.dirname(filename)
            if not os.listdir(containing_dir):
                os.rmdir(containing_dir)

    def delete_all_messages(self):
        """Remove ALL stored messages."""
        self.set_pending_offset(0)
        for filename in self._walk_messages():
            os.unlink(filename)

    def is_pending(self, message_id):
        """Return bool indicating if C{message_id} still hasn't been delivered.

        @param message_id: Identifier returned by the L{add()} method.
        """
        i = 0
        pending_offset = self.get_pending_offset()
        for filename in self._walk_messages(exclude=BROKEN):
            flags = self._get_flags(filename)
            if ((HELD in flags or i >= pending_offset) and
                os.stat(filename).st_ino == message_id):
                return True
            if BROKEN not in flags and HELD not in flags:
                i += 1
        return False

    def add(self, message):
        """Queue a message for delivery.

        @return: message_id, which is an identifier for the added message.
        """
        filename = self._get_next_message_filename()

        return self._write_message(message, filename)

    def update(self, message):
        return self._write_message(message)

    def _get_next_message_filename(self):
        message_dirs = self._get_sorted_filenames()
        if message_dirs:
            newest_dir = message_dirs[-1]
        else:
            os.makedirs(self._message_dir("0"))
            newest_dir = "0"

        message_filenames = self._get_sorted_filenames(newest_dir)
        if not message_filenames:
            filename = self._message_dir(newest_dir, "0")
        elif len(message_filenames) < self._directory_size:
            filename = str(int(message_filenames[-1].split("_")[0]) + 1)
            filename = self._message_dir(newest_dir, filename)
        else:
            newest_dir = self._message_dir(str(int(newest_dir) + 1))
            os.makedirs(newest_dir)
            filename = posixpath.join(newest_dir, "0")

        return filename

    def _walk_pending_messages(self):
        """Walk the files which are definitely pending."""
        pending_offset = self.get_pending_offset()
        filenames = self._walk_messages(exclude=HELD + BROKEN)
        for index, filename in enumerate(filenames):
            if index >= pending_offset:
                yield filename

    def _walk_messages(self, exclude=None):
        if exclude:
            exclude = set(exclude)
        message_dirs = self._get_sorted_filenames()
        for message_dir in message_dirs:
            for filename in self._get_sorted_filenames(message_dir):
                flags = set(self._get_flags(filename))
                if (not exclude or not exclude & flags):
                    yield self._message_dir(message_dir, filename)

    def _get_sorted_filenames(self, dir=""):
        message_files = [x for x in os.listdir(self._message_dir(dir))
                         if not x.endswith(".tmp")]
        message_files = sorted(message_files,
            key=lambda x: int(x.split("_")[0]))
        return message_files

    def _message_dir(self, *args):
        return posixpath.join(self._directory, *args)

    def _get_content(self, filename):
        file = open(filename, "rb")
        try:
            return file.read()
        finally:
            safe_close(file, safe=self.safe_file_closing)

    def _get_flags(self, path):
        basename = posixpath.basename(path)
        if "_" in basename:
            return basename.split("_")[1]
        return ""

    def _set_flags(self, path, flags):
        dirname, basename = posixpath.split(path)
        new_path = posixpath.join(dirname, basename.split("_")[0])
        if flags:
            new_path += "_" + "".join(sorted(set(flags)))
        os.rename(path, new_path)
        return new_path

    def _add_flags(self, path, flags):
        self._set_flags(path, self._get_flags(path) + flags)

    def _load_message(self, data):
        return bpickle.loads(data)

    def _dump_message(self, message):
        return bpickle.dumps(message)

    def _read_message(self, filename, cache=False):
        #cache basically indicates whether the caller cares about having "data"
        if cache and filename in self._message_cache:
            return Message(self._message_cache[filename], filename)

        data = self._get_content(filename)
        message = self._load_message(data)
        return Message(message, filename)

    def _write_message(self, message, filename=None):
        if filename is None:
            filename = message.filename

        message_data = self._dump_message(message)

        file = open(filename + ".tmp", "wb")
        file.write(message_data)
        safe_close(file, safe=self.safe_file_closing)

        os.rename(filename + ".tmp", filename)

        #Strip the big data element and shove it in the cache

        temp_message = dict(message)
        if "data" in temp_message:
            temp_message["data"] = None

        self._message_cache[filename] = temp_message

        # For now we use the inode as the message id, as it will work
        # correctly even faced with holding/unholding.  It will break
        # if the store is copied over for some reason, but this shouldn't
        # present an issue given the current uses.  In the future we
        # should have a nice transactional storage (e.g. sqlite) which
        # will offer a more strong primary key.
        return os.stat(filename).st_ino


def got_next_sequence(message_store, next_sequence):
    """Our peer has told us what it expects our next message's sequence to be.

    Call this with the message store and sequence number that the peer
    wants next; this will do various things based on what *this* side
    has in its outbound queue store.

    1. The peer expects a sequence greater than what we last
       sent. This is the common case and generally it should be
       expecting last_sent_sequence+len(messages_sent)+1.

    2. The peer expects a sequence number our side has already sent,
       and we no longer have that message. In this case, just send
       *all* messages we have, including the previous generation,
       starting at the sequence number the peer expects (meaning that
       messages have probably been lost).

    3. The peer expects a sequence number we already sent, and we
       still have that message cached. In this case, we send starting
       from that message.

    If the next sequence from the server refers to a message older than
    we have, then L{ANCIENT} will be returned.
    """
    ret = None
    old_sequence = message_store.get_sequence()
    if next_sequence > old_sequence:
        message_store.delete_old_messages()
        pending_offset = next_sequence - old_sequence
    elif next_sequence < (old_sequence - message_store.get_pending_offset()):
        # "Ancient": The other side wants messages we don't have,
        # so let's just reset our counter to what it expects.
        pending_offset = 0
        ret = ANCIENT
    else:
        # No messages transferred, or
        # "Old": We'll try to send these old messages that the
        # other side still wants.
        pending_offset = (message_store.get_pending_offset() + next_sequence
                          - old_sequence)

    message_store.set_pending_offset(pending_offset)
    message_store.set_sequence(next_sequence)
    return ret
