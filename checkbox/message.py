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
import itertools
import logging
import os

from checkbox.contrib import bpickle
from checkbox.schema import Any, Constant, Float, KeyDict, String


HELD = "h"
BROKEN = "b"


class MessageStore(object):
    """A message store which stores its messages in a file system hierarchy."""

    def __init__(self, persist, directory, directory_size=1000):
        self._directory = directory
        self._directory_size = directory_size
        self._schemas = {}
        self._original_persist = persist
        self._persist = persist.root_at("message-store")
        message_dir = self._message_dir()
        if not os.path.isdir(message_dir):
            os.makedirs(message_dir)

    def commit(self):
        """Save metadata to disk."""
        self._original_persist.save()

    def set_accepted_types(self, types):
        """Specify the types of messages that the server will expect from us.

        If messages are added to the store which are not currently
        accepted, they will be saved but ignored until their type is
        accepted.
        """
        assert type(types) in (tuple, list, set)
        self._persist.set("accepted-types", sorted(set(types)))
        self._reprocess_holding()

    def get_accepted_types(self):
        return self._persist.get("accepted-types", ())

    def accepts(self, type):
        return type in self.get_accepted_types()

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

    def get_server_sequence(self):
        """
        Get the sequence number of the message that we will ask the server to
        send to us on the next exchange.
        """
        return self._persist.get("server_sequence", 0)

    def set_server_sequence(self, number):
        """
        Set the sequence number of the message that we will ask the server to
        send to us on the next exchange.
        """
        self._persist.set("server_sequence", number)

    def get_pending_offset(self):
        return self._persist.get("pending_offset", 0)

    def set_pending_offset(self, val):
        """
        Set the offset into the message pool to consider assigned to the
        current sequence number as returned by l{get_sequence}.
        """
        self._persist.set("pending_offset", val)

    def add_pending_offset(self, val):
        self.set_pending_offset(self.get_pending_offset() + val)

    def count_pending_messages(self):
        """Return the number of pending messages."""
        return sum(1 for x in self._walk_pending_messages())

    def get_pending_messages(self, max=None):
        """Get any pending messages that aren't being held, up to max."""
        accepted_types = self.get_accepted_types()
        messages = []
        for filename in self._walk_pending_messages():
            if max is not None and len(messages) >= max:
                break
            data = self._get_content(self._message_dir(filename))
            try:
                message = bpickle.loads(data)
            except ValueError, e:
                logging.exception(e)
                self._add_flags(filename, BROKEN)
            else:
                if message["type"] not in accepted_types:
                    self._add_flags(filename, HELD)
                else:
                    messages.append(message)
        return messages

    def get_message(self, message_id):
        """Delete a message given the corresponding id."""
        message = None
        for filename in self._walk_messages(exclude=BROKEN):
            if os.stat(filename).st_ino == message_id:
                content = self._get_content(filename)
                message = bpickle.loads(content)

        return message

    def delete_message(self, message_id):
        """Delete a message given the corresponding id."""
        for filename in self._walk_messages():
            if os.stat(filename).st_ino == message_id:
                os.unlink(filename)

    def delete_old_messages(self):
        """Delete messages which are unlikely to be needed in the future."""
        filenames = self._get_sorted_filenames()
        for fn in itertools.islice(self._walk_messages(exclude=HELD+BROKEN),
                                   self.get_pending_offset()):
            os.unlink(fn)
            containing_dir = os.path.split(fn)[0]
            if not os.listdir(containing_dir):
                os.rmdir(containing_dir)

    def delete_all_messages(self):
        """Remove ALL stored messages."""
        self.set_pending_offset(0)
        for filename in self._walk_messages():
            os.unlink(filename)

    def add_schema(self, schema):
        """Add a schema to be applied to messages of the given type.

        The schema must be an instance of L{landscape.schema.Message}.
        """
        self._schemas[schema.type] = schema

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
        assert "type" in message
        message = self._schemas[message["type"]].coerce(message)

        message_data = bpickle.dumps(message)

        filename = self._get_next_message_filename()

        descriptor = open(filename + ".tmp", "w")
        descriptor.write(message_data)
        descriptor.close()
        os.rename(filename + ".tmp", filename)

        if not self.accepts(message["type"]):
            filename = self._set_flags(filename, HELD)

        # For now we use the inode as the message id, as it will work
        # correctly even faced with holding/unholding.  It will break
        # if the store is copied over for some reason, but this shouldn't
        # present an issue given the current uses.  In the future we
        # should have a nice transactional storage (e.g. sqlite) which
        # will offer a more strong primary key.
        message_id = os.stat(filename).st_ino

        return message_id

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
            filename = os.path.join(newest_dir, "0")

        return filename

    def _walk_pending_messages(self):
        """Walk the files which are definitely pending."""
        pending_offset = self.get_pending_offset()
        for i, filename in enumerate(self._walk_messages(exclude=HELD+BROKEN)):
            if i >= pending_offset:
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
        return os.path.join(self._directory, *args)

    def _get_content(self, filename):
        descriptor = open(filename)
        try:
            return descriptor.read()
        finally:
            descriptor.close()

    def _reprocess_holding(self):
        """
        Unhold accepted messages left behind, and hold unaccepted
        pending messages.
        """
        offset = 0
        pending_offset = self.get_pending_offset()
        accepted_types = self.get_accepted_types()
        for old_filename in self._walk_messages():
            flags = self._get_flags(old_filename)
            try:
                message = bpickle.loads(self._get_content(old_filename))
            except ValueError, e:
                logging.exception(e)
                if HELD not in flags:
                    offset += 1
            else:
                accepted = message["type"] in accepted_types
                if HELD in flags:
                    if accepted:
                        new_filename = self._get_next_message_filename()
                        os.rename(old_filename, new_filename)
                        self._set_flags(new_filename, set(flags)-set(HELD))
                else:
                    if not accepted and offset >= pending_offset:
                        self._set_flags(old_filename, set(flags)|set(HELD))
                    offset += 1

    def _get_flags(self, path):
        basename = os.path.basename(path)
        if "_" in basename:
            return basename.split("_")[1]
        return ""

    def _set_flags(self, path, flags):
        dirname, basename = os.path.split(path)
        new_path = os.path.join(dirname, basename.split("_")[0])
        if flags:
            new_path += "_"+"".join(sorted(set(flags)))
        os.rename(path, new_path)
        return new_path

    def _add_flags(self, path, flags):
        self._set_flags(path, self._get_flags(path)+flags)



class Message(KeyDict):
    """
    Like {KeyDict}, but with three predefined keys: C{type}, C{api},
    and C{timestamp}. Of these, C{api} and C{timestamp} are optional.


    @param type: The type of the message. The C{type} key will need to
        match this as a constant.

    @param schema: A dict of additional schema in a format L{KeyDict}
        will accept.
    @param optional: An optional list of keys that should be optional.
    """
    def __init__(self, type, schema, optional=None):
        self.type = type
        schema["timestamp"] = Float()
        schema["api"] = Any(String(), Constant(None))
        schema["type"] = Constant(type)
        if optional is not None:
            optional.extend(["timestamp", "api"])
        else:
            optional = ["timestamp", "api"]
        super(Message, self).__init__(schema, optional=optional)
