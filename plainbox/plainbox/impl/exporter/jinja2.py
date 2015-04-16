# This file is part of Checkbox.
#
# Copyright 2015 Canonical Ltd.
# Written by:
#   Maciej Kisielewski <maciej.kisielewski@canonical.com>
#   Sylvain Pineau <sylvain.pineau@canonical.com>
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
:mod:`plainbox.impl.exporter.jinja2` -- exporter using jinja2 templates
=======================================================================

.. warning::
    THIS MODULE DOES NOT HAVE A STABLE PUBLIC API
"""

from jinja2 import Environment, FileSystemLoader, Markup
from pkg_resources import resource_filename

from plainbox.abc import ISessionStateExporter


class Jinja2SessionStateExporter(ISessionStateExporter):

    """Session state exporter that renders output using jinja2 template."""

    supported_option_list = ()

    def __init__(self, jinja2_template, option_list=None, extra_paths=()):
        """
        Initialize a new Jinja2SessionStateExporter with given arguments.

        :param option_list:
            List of options that template might use to fine-tune rendering.
        :param jinja2_template:
            Filename of a Jinja2 template that will be loaded using the
            Jinja2 FileSystemLoader.
        :param extra_paths:
            List of additional paths to load Jinja2 templates

        """
        self.option_list = option_list
        paths = [resource_filename("plainbox", "data/report/")]
        paths.extend(extra_paths)
        loader = FileSystemLoader(paths)
        env = Environment(loader=loader)

        def include_file(name):
            # This helper function insert static files literally into Jinja
            # templates without parsing them.
            return Markup(loader.get_source(env, name)[0])

        self.template = env.get_template(jinja2_template)
        env.globals['include_file'] = include_file

    def dump(self, data, stream):
        """
        Render report using jinja2 and dump it to stream.

        :param data:
            Dict to be used when rendering template instance
        :param stream:
            Byte stream to write to.

        """
        self.template.stream(data).dump(stream, encoding='utf-8')

    def dump_from_session_manager(self, session_manager, stream):
        """
        Extract data from session_manager and dump it into the stream.

        :param session_manager:
            SessionManager instance that manages session to be exported by
            this exporter
        :param stream:
            Byte stream to write to.

        """
        data = {
            'manager': session_manager,
            'options': self.option_list
        }
        self.dump(data, stream)

    def get_session_data_subset(self, session_manager):
        """Compute a subset of session data."""
        return {
            'manager': session_manager,
            'options': self.option_list,
        }
