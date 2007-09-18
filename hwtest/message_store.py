import os
import logging

from hwtest.contrib import bpickle


BROKEN = "b"

class MessageStore(object):

    def __init__(self, reactor, persist, directory):
        self._reactor = reactor
        self._persist = persist.root_at("message-store")
        self._directory = directory

        message_dir = self._message_dir()
        if not os.path.isdir(message_dir):
            os.makedirs(message_dir)

    def get_secure_id(self):
        return self._persist.get("secure_id")

    def set_secure_id(self, secure_id):
        return self._persist.set("secure_id", secure_id)

    def get_pending_messages(self):
        messages = []
        for i, filename in enumerate(self._walk_messages(exclude=BROKEN)):
            data = self._get_content(self._message_dir(filename))
            try:
                message = bpickle.loads(data)
            except ValueError, e:
                logging.exception(e)
                self._add_flags(filename, BROKEN)
            else:
                messages.append(message)
        return messages

    def add(self, message, urgent=False):
        message_data = bpickle.dumps(message)

        filename = self._get_next_message_filename()

        fd = file(filename + ".tmp", "w")
        fd.write(message_data)
        fd.close()
        os.rename(filename + ".tmp", filename)

    def delete(self):
        filenames = self._get_sorted_filenames()
        for fn in self._walk_messages(exclude=BROKEN):
            os.unlink(fn)
            containing_dir = os.path.split(fn)[0]
            if not os.listdir(containing_dir):
                os.rmdir(containing_dir)

    def _get_content(self, filename):
        fd = file(filename, "r")
        try:
            return fd.read()
        finally:
            fd.close()

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
        else:
            filename = str(int(message_filenames[-1].split("_")[0]) + 1)
            filename = self._message_dir(newest_dir, filename)

        return filename

    def _get_sorted_filenames(self, dir=""):
        message_files = [x for x in os.listdir(self._message_dir(dir))
                         if not x.endswith(".tmp")]
        message_files.sort(key=lambda x: int(x.split("_")[0]))
        return message_files

    def _message_dir(self, *args):
        return os.path.join(self._directory, *args)

    def _walk_messages(self, exclude=None):
        if exclude:
            exclude = set(exclude)
        message_dirs = self._get_sorted_filenames()
        for message_dir in message_dirs:
            for filename in self._get_sorted_filenames(message_dir):
                flags = set(self._get_flags(filename))
                if (not exclude or not exclude & flags):
                    yield self._message_dir(message_dir, filename)

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

    def _add_flags(self, path, flags):
        self._set_flags(path, self._get_flags(path)+flags)
