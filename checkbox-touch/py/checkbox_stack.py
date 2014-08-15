# This file is part of Checkbox.
#
# Copyright 2014 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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
"""
:mod:`checkbox_stack` -- Python Interface to Checkbox QML Stack
===============================================================

This module is a part of the implementation of the Checkbox QML Stack. It is
being imported at startup of all QML applications that are using Checkbox.
"""
import builtins
import threading

import plainbox


class RemoteObjectLifecycleManager:
    """
    Remote object life-cycle manager

    This class aids in handling non-trivial objects that are referenced from
    QML (via pyotherside) but really stored on the python side.
    """

    def __init__(self):
        self._count = 0
        self._handle_map = {}
        self._lock = threading.Lock()

    def unref(self, handle: int):
        """
        Remove a reference represented by the specified handle
        """
        with self._lock:
            del self._handle_map[handle]

    def ref(self, obj: object) -> int:
        """
        Store a reference to an object and return the handle
        """
        with self._lock:
            self._count += 1
            handle = self._count
            self._handle_map[handle] = obj
            return handle

    def invoke(self, handle: int, func: str, args):
        with self._lock:
            obj = self._handle_map[handle]
            impl = getattr(obj, func)
            retval = impl(*args)
            # print("(py_invoke) returning", retval)
            return retval


_manager = RemoteObjectLifecycleManager()

# top-level functions exposed for pyotherside's simplicity
py_ref = builtins.py_ref = _manager.ref
builtins.py_unref = _manager.unref
builtins.py_invoke = _manager.invoke


class PlainBox:
    """
    Wrapper around the whole plainbox library
    """

    def __init__(self):
        self.provider_list = []
        self.session_list = []
        self.config = None

    @classmethod
    def create_and_get_handle(cls):
        """
        Create an instance of the high-level PlainBox object

        :returns:
            A handle to a fresh instance of :class:`PlainBox`
        """
        return py_ref(cls())

    def get_version(self) -> str:
        """
        Get the version of the PlainBox library
        """
        from plainbox.impl.clitools import ToolBase
        return ToolBase.format_version_tuple(plainbox.__version__)


create_plainbox_object = PlainBox.create_and_get_handle
