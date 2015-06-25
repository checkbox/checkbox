# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
# Written by:
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
:mod:`plainbox.impl.exporter.xlsx`
==================================

XLSX exporter

.. warning::
    THIS MODULE DOES NOT HAVE A STABLE PUBLIC API
"""

from base64 import standard_b64decode
from collections import defaultdict, OrderedDict
import re

from xlsxwriter.workbook import Workbook
from xlsxwriter.utility import xl_rowcol_to_cell

from plainbox.abc import IJobResult
from plainbox.i18n import gettext as _, ngettext
from plainbox.impl.exporter import SessionStateExporterBase
from plainbox.impl.result import OUTCOME_METADATA_MAP as OMM


class XLSXSessionStateExporter(SessionStateExporterBase):
    """
    Session state exporter creating XLSX documents

    The hardware devices are extracted from the content of the following
    attachment:

    * 2013.com.canonical.certification::lspci_attachment

    The following resource jobs are needed to populate the system info section
    of this report:

    * 2013.com.canonical.certification::dmi
    * 2013.com.canonical.certification::device
    * 2013.com.canonical.certification::cpuinfo
    * 2013.com.canonical.certification::meminfo
    * 2013.com.canonical.certification::package
    """

    OPTION_WITH_SYSTEM_INFO = 'with-sys-info'
    OPTION_WITH_SUMMARY = 'with-summary'
    OPTION_WITH_DESCRIPTION = 'with-job-description'
    OPTION_WITH_TEXT_ATTACHMENTS = 'with-text-attachments'
    OPTION_WITH_UNIT_CATEGORIES = 'with-unit-categories'

    SUPPORTED_OPTION_LIST = (
        OPTION_WITH_SYSTEM_INFO,
        OPTION_WITH_SUMMARY,
        OPTION_WITH_DESCRIPTION,
        OPTION_WITH_TEXT_ATTACHMENTS,
        OPTION_WITH_UNIT_CATEGORIES,
    )

    def __init__(self, option_list=None, exporter_unit=None):
        """
        Initialize a new XLSXSessionStateExporter.
        """
        # Super-call with empty option list
        super(XLSXSessionStateExporter, self).__init__(())
        # All the "options" are simply a required configuration element and are
        # not optional in any way. There is no way to opt-out.
        if option_list is None:
            option_list = ()
        for option in option_list:
            if option not in self.supported_option_list:
                raise ValueError(_("Unsupported option: {}").format(option))
        if exporter_unit:
            for option in exporter_unit.option_list:
                if option not in self.supported_option_list:
                    raise ValueError(
                        _("Unsupported option: {}").format(option))
        self._option_list = (
            SessionStateExporterBase.OPTION_WITH_IO_LOG,
            SessionStateExporterBase.OPTION_FLATTEN_IO_LOG,
            SessionStateExporterBase.OPTION_WITH_COMMENTS,
            SessionStateExporterBase.OPTION_WITH_JOB_DEFS,
            SessionStateExporterBase.OPTION_WITH_JOB_VIA,
            SessionStateExporterBase.OPTION_WITH_JOB_HASH,
            SessionStateExporterBase.OPTION_WITH_RESOURCE_MAP,
            SessionStateExporterBase.OPTION_WITH_ATTACHMENTS,
            SessionStateExporterBase.OPTION_WITH_CATEGORY_MAP,
            SessionStateExporterBase.OPTION_WITH_CERTIFICATION_STATUS,
        )
        self._option_list += tuple(option_list)
        if exporter_unit:
            self._option_list += tuple(exporter_unit.option_list)
        self.total_pass = 0
        self.total_fail = 0
        self.total_skip = 0
        self.total = 0

    def _set_formats(self):
        # Main Title format (Orange)
        self.format01 = self.workbook.add_format({
            'align': 'left', 'size': 24, 'font_color': '#DC4C00',
        })
        # Default font
        self.format02 = self.workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'size': 10,
        })
        # Titles
        self.format03 = self.workbook.add_format({
            'align': 'left', 'size': 12, 'bold': 1,
        })
        # Titles + borders
        self.format04 = self.workbook.add_format({
            'align': 'left', 'size': 12, 'bold': 1, 'border': 1
        })
        # System info with borders
        self.format05 = self.workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'text_wrap': 1, 'size': 8,
            'border': 1,
        })
        # System info with borders, grayed out background
        self.format06 = self.workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'text_wrap': 1, 'size': 8,
            'border': 1, 'bg_color': '#E6E6E6',
        })
        # Headlines (center)
        self.format07 = self.workbook.add_format({
            'align': 'center', 'size': 10, 'bold': 1,
        })
        # Table rows without borders
        self.format08 = self.workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'text_wrap': 1, 'size': 8,
        })
        # Table rows without borders, grayed out background
        self.format09 = self.workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'text_wrap': 1, 'size': 8,
            'bg_color': '#E6E6E6',
        })
        # Green background / Size 8
        self.format10 = self.workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'size': 8,
            'bg_color': 'lime', 'border': 1, 'border_color': 'white',
        })
        # Red background / Size 8
        self.format11 = self.workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'size': 8,
            'bg_color': 'red', 'border': 1, 'border_color': 'white',
        })
        # Gray background / Size 8
        self.format12 = self.workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'text_wrap': 1, 'size': 8,
            'bg_color': 'gray', 'border': 1, 'border_color': 'white',
        })
        # Dictionary with formats for each possible outcome
        self.outcome_format_map = {
            outcome_info.value: self.workbook.add_format({
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': '1',
                'size': 8,
                'bg_color': outcome_info.color_hex,
                'border': 1,
                'border_color': 'white'
            }) for outcome_info in OMM.values()
        }
        # Attachments
        self.format13 = self.workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'text_wrap': 1, 'size': 8,
            'font': 'Courier New',
        })
        # Invisible man
        self.format14 = self.workbook.add_format({'font_color': 'white'})
        # Headlines (left-aligned)
        self.format15 = self.workbook.add_format({
            'align': 'left', 'size': 10, 'bold': 1,
        })
        # Table rows without borders, indent level 1
        self.format16 = self.workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'size': 8, 'indent': 1,
        })
        # Table rows without borders, grayed out background, indent level 1
        self.format17 = self.workbook.add_format({
            'align': 'left', 'valign': 'vcenter', 'size': 8,
            'bg_color': '#E6E6E6', 'indent': 1,
        })
        # Table rows without borders (center)
        self.format18 = self.workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'size': 8,
        })
        # Table rows without borders, grayed out background (center)
        self.format19 = self.workbook.add_format({
            'align': 'center', 'valign': 'vcenter', 'size': 8,
            'bg_color': '#E6E6E6',
        })

    def _hw_collection(self, data):
        hw_info = defaultdict(lambda: 'NA')
        resource = '2013.com.canonical.certification::dmi'
        if resource in data['resource_map']:
            result = [
                '{} {} ({})'.format(
                    i.get('vendor'), i.get('product'), i.get('version'))
                for i in data["resource_map"][resource]
                if i.get('category') == 'SYSTEM']
            if result:
                hw_info['platform'] = result.pop()
            result = [
                '{}'.format(i.get('version'))
                for i in data["resource_map"][resource]
                if i.get('category') == 'BIOS']
            if result:
                hw_info['bios'] = result.pop()
        resource = '2013.com.canonical.certification::cpuinfo'
        if resource in data['resource_map']:
            result = ['{} x {}'.format(i['model'], i['count'])
                      for i in data["resource_map"][resource]]
            if result:
                hw_info['processors'] = result.pop()
        resource = '2013.com.canonical.certification::lspci_attachment'
        if resource in data['attachment_map']:
            lspci = data['attachment_map'][resource]
            content = standard_b64decode(lspci.encode()).decode("UTF-8")
            match = re.search('ISA bridge.*?:\s(?P<chipset>.*?)\sLPC', content)
            if match:
                hw_info['chipset'] = match.group('chipset')
            match = re.search(
                'Audio device.*?:\s(?P<audio>.*?)\s\[\w+:\w+]', content)
            if match:
                hw_info['audio'] = match.group('audio')
            match = re.search(
                'Ethernet controller.*?:\s(?P<nic>.*?)\s\[\w+:\w+]', content)
            if match:
                hw_info['nic'] = match.group('nic')
            match = re.search(
                'Network controller.*?:\s(?P<wireless>.*?)\s\[\w+:\w+]',
                content)
            if match:
                hw_info['wireless'] = match.group('wireless')
            for i, match in enumerate(re.finditer(
                'VGA compatible controller.*?:\s(?P<video>.*?)\s\[\w+:\w+]',
                content), start=1
            ):
                hw_info['video{}'.format(i)] = match.group('video')
            vram = 0
            for match in re.finditer(
                    'Memory.+ prefetchable\) \[size=(?P<vram>\d+)M\]',
                    content):
                vram += int(match.group('vram'))
            if vram:
                hw_info['vram'] = '{} MiB'.format(vram)
        resource = '2013.com.canonical.certification::meminfo'
        if resource in data['resource_map']:
            result = ['{} GiB'.format(format(int(i['total']) / 1073741824,
                      '.1f')) for i in data["resource_map"][resource]]
            if result:
                hw_info['memory'] = result.pop()
        bluetooth = self._get_bluetooth_product_or_path(data)
        if bluetooth:
                hw_info['bluetooth'] = bluetooth
        return hw_info

    def _get_resource_list(self, data, resource_id):
        """
        Get a list of resource objects associated with the specified job
        (resource) identifier

        :param data:
            Exporter data
        :param resource_id:
            Identifier of the job / resource
        :returns:
            A list of matching resource objects. If there are no resources of
            that kind then an empty list list returned.
        """
        resource_map = data.get('resource_map')
        if not resource_map:
            return []
        return resource_map.get(resource_id, [])

    def _get_bluetooth_product_or_path(
            self, data,
            resource_id='2013.com.canonical.certification::device'):
        """
        Get the 'product' or 'path' of the first bluetooth device.

        :param data:
            Exporter data
        :param resource_id:
            (optional) Identifier of the device resource.
        :returns:
            The 'product' attribute, or the 'path' attribute or None if no such
            device can be found.

        This method finds the name of the 'product' or 'path' attributes (first
        available one wins) associated with a resource that has a 'category'
        attribute equal to BLUETOOTH. The resource is looked using the supplied
        (default) resource identifier.
        """
        for resource in self._get_resource_list(data, resource_id):
            if resource.get('category') != 'BLUETOOTH':
                continue
            if 'product' in resource:
                return resource['product']
            if 'path' in resource:
                return resource['path']

    def write_systeminfo(self, data):
        self.worksheet1.set_column(0, 0, 4)
        self.worksheet1.set_column(1, 1, 34)
        self.worksheet1.set_column(2, 3, 58)
        hw_info = self._hw_collection(data)
        self.worksheet1.write(5, 1, _('Platform Name'), self.format03)
        self.worksheet1.write(5, 2, hw_info['platform'], self.format03)
        self.worksheet1.write(7, 1, _('BIOS'), self.format04)
        self.worksheet1.write(7, 2, hw_info['bios'], self.format06)
        self.worksheet1.write(8, 1, _('Processors'), self.format04)
        self.worksheet1.write(8, 2, hw_info['processors'], self.format05)
        self.worksheet1.write(9, 1, _('Chipset'), self.format04)
        self.worksheet1.write(9, 2, hw_info['chipset'], self.format06)
        self.worksheet1.write(10, 1, _('Memory'), self.format04)
        self.worksheet1.write(10, 2, hw_info['memory'], self.format05)
        # TRANSLATORS: on board as in 'built in card'
        self.worksheet1.write(11, 1, _('Video (on board)'), self.format04)
        self.worksheet1.write(11, 2, hw_info['video1'], self.format06)
        # TRANSLATORS: add-on as in dedicated graphics card
        self.worksheet1.write(12, 1, _('Video (add-on)'), self.format04)
        self.worksheet1.write(12, 2, hw_info['video2'], self.format05)
        self.worksheet1.write(13, 1, _('Video memory'), self.format04)
        self.worksheet1.write(13, 2, hw_info['vram'], self.format06)
        self.worksheet1.write(14, 1, _('Audio'), self.format04)
        self.worksheet1.write(14, 2, hw_info['audio'], self.format05)
        # TRANSLATORS: NIC is network interface card
        self.worksheet1.write(15, 1, _('NIC'), self.format04)
        self.worksheet1.write(15, 2, hw_info['nic'], self.format06)
        # TRANSLTORS: Wireless as in wireless network cards
        self.worksheet1.write(16, 1, _('Wireless'), self.format04)
        self.worksheet1.write(16, 2, hw_info['wireless'], self.format05)
        self.worksheet1.write(17, 1, _('Bluetooth'), self.format04)
        self.worksheet1.write(17, 2, hw_info['bluetooth'], self.format06)
        resource = '2013.com.canonical.certification::package'
        if resource in data["resource_map"]:
            self.worksheet1.write(
                19, 1, _('Packages Installed'), self.format03)
            self.worksheet1.write_row(
                21, 1, [_('Name'), _('Version')], self.format07)
            for i in range(20, 22):
                self.worksheet1.set_row(
                    i, None, None, {'level': 1, 'hidden': True}
                )
            for i, pkg in enumerate(data["resource_map"][resource]):
                self.worksheet1.write_row(
                    22 + i, 1,
                    [pkg['name'], pkg['version']],
                    self.format08 if i % 2 else self.format09
                )
                self.worksheet1.set_row(
                    22 + i, None, None, {'level': 1, 'hidden': True}
                )
            self.worksheet1.set_row(
                22+len(data["resource_map"][resource]),
                None, None, {'collapsed': True}
            )

    def write_summary(self, data):
        if self.total != 0:
            pass_rate = "{:.2f}%".format(self.total_pass / self.total * 100)
            fail_rate = "{:.2f}%".format(self.total_fail / self.total * 100)
            skip_rate = "{:.2f}%".format(self.total_skip / self.total * 100)
        else:
            pass_rate = _("N/A")
            fail_rate = _("N/A")
            skip_rate = _("N/A")
        self.worksheet2.set_column(0, 0, 5)
        self.worksheet2.set_column(1, 1, 2)
        self.worksheet2.set_column(3, 3, 27)
        self.worksheet2.write(3, 1, _('Failures summary'), self.format03)
        self.worksheet2.write(
            4, 1, OMM['pass'].unicode_sigil, self.outcome_format_map['pass'])
        self.worksheet2.write(
            4, 2, (
                ngettext('{} Test passed', '{} Tests passed',
                         self.total_pass).format(self.total_pass)
                + " - "
                + _('Success Rate: {} ({}/{})').format(
                    pass_rate, self.total_pass, self.total)
            ), self.format02)
        self.worksheet2.write(
            5, 1, OMM['fail'].unicode_sigil, self.outcome_format_map['fail'])
        self.worksheet2.write(
            5, 2, (
                ngettext('{} Test failed', '{} Tests failed',
                         self.total_fail).format(self.total_fail)
                + ' - '
                + _('Failure Rate: {} ({}/{})').format(
                    fail_rate, self.total_fail, self.total)
            ), self.format02)
        self.worksheet2.write(
            6, 1, OMM['skip'].unicode_sigil, self.outcome_format_map['skip'])
        self.worksheet2.write(
            6, 2, (
                ngettext('{} Test skipped', '{} Tests skipped',
                         self.total_skip).format(self.total_skip)
                + ' - '
                + _('Skip Rate: {} ({}/{})').format(
                    skip_rate, self.total_skip, self.total)
            ), self.format02)
        self.worksheet2.write_column(
            'L3', [OMM['fail'].tr_label,
                   OMM['skip'].tr_label,
                   OMM['pass'].tr_label], self.format14)
        self.worksheet2.write_column(
            'M3', [self.total_fail, self.total_skip, self.total_pass],
            self.format14)
        # Configure the series.
        chart = self.workbook.add_chart({'type': 'pie'})
        chart.set_legend({'position': 'none'})
        chart.add_series({
            'points': [
                {'fill': {'color': OMM['fail'].color_hex}},
                {'fill': {'color': OMM['skip'].color_hex}},
                {'fill': {'color': OMM['pass'].color_hex}},
            ],
            'categories': '=' + _("Summary") + '!$L$3:$L$5',
            'values': '=' + _("Summary") + '!$M$3:$M$5'}
        )
        # Insert the chart into the worksheet.
        self.worksheet2.insert_chart('F4', chart, {
            'x_offset': 0, 'y_offset': 10, 'x_scale': 0.50, 'y_scale': 0.50
        })

    def _set_category_status(self, result_map, via, child):
        for parent in [j for j in result_map if result_map[j]['hash'] == via]:
            if 'category_status' not in result_map[parent]:
                result_map[parent]['category_status'] = None
            child_status = result_map[child]['outcome']
            if 'category_status' in result_map[child]:
                child_status = result_map[child]['category_status']
            # Ignore categories without any child
            elif result_map[child]['plugin'] == 'local':
                continue
            if child_status == IJobResult.OUTCOME_FAIL:
                result_map[parent]['category_status'] = IJobResult.OUTCOME_FAIL
            elif (
                child_status == IJobResult.OUTCOME_PASS and
                result_map[parent]['category_status'] !=
                    IJobResult.OUTCOME_FAIL
            ):
                result_map[parent]['category_status'] = IJobResult.OUTCOME_PASS
            elif (
                result_map[parent]['category_status'] not in
                (IJobResult.OUTCOME_PASS, IJobResult.OUTCOME_FAIL)
            ):
                result_map[parent]['category_status'] = IJobResult.OUTCOME_SKIP

    def _tree(self, result_map, category_map):
        res = {}
        tmp_result_map = {}
        for job_name in result_map:
            if result_map[job_name]['plugin'] in ('resource', 'attachment'):
                continue
            category = category_map[result_map[job_name]['category_id']]
            if category not in res:
                tmp_result_map[category] = {}
                tmp_result_map[category]['category_status'] = None
                tmp_result_map[category]['plugin'] = 'local'
                tmp_result_map[category]['summary'] = category
                res[category] = {}
            res[category][job_name] = {}
            # Generate categories status
            child_status = result_map[job_name]['outcome']
            if child_status == IJobResult.OUTCOME_FAIL:
                tmp_result_map[category]['category_status'] = \
                    IJobResult.OUTCOME_FAIL
            elif (
                child_status == IJobResult.OUTCOME_PASS and
                tmp_result_map[category]['category_status'] !=
                    IJobResult.OUTCOME_FAIL
            ):
                tmp_result_map[category]['category_status'] = \
                    IJobResult.OUTCOME_PASS
            elif (
                tmp_result_map[category]['category_status'] not in
                (IJobResult.OUTCOME_PASS, IJobResult.OUTCOME_FAIL)
            ):
                tmp_result_map[category]['category_status'] = \
                    IJobResult.OUTCOME_SKIP
        result_map.update(tmp_result_map)
        return res, 2

    def _legacy_tree(self, result_map, via=None, level=0, max_level=0):
        res = {}
        for job_name in [j for j in result_map if result_map[j]['via'] == via]:
            if result_map[job_name]['plugin'] in ('resource', 'attachment'):
                continue
            level += 1
            # Find the maximum depth of the test tree
            if level > max_level:
                max_level = level
            res[job_name], max_level = self._legacy_tree(
                result_map, result_map[job_name]['hash'], level, max_level)
            # Generate parent categories status
            if via is not None:
                self._set_category_status(result_map, via, job_name)
            level -= 1
        return res, max_level

    def _write_job(self, tree, result_map, max_level, level=0):
        for job, children in OrderedDict(
                sorted(
                    tree.items(),
                    key=lambda t: 'z' + t[0] if t[1] else 'a' + t[0])).items():
            if (result_map[job]['plugin'] == 'local' and
                    not result_map[job].get('category_status')):
                continue
            self._lineno += 1
            if children:
                self.worksheet3.write(
                    self._lineno, level + 1,
                    result_map[job]['summary'], self.format15)
                outcome = result_map[job]['category_status']
                self.worksheet3.write(
                    self._lineno, max_level + 2,
                    OMM[outcome].tr_label, self.outcome_format_map[outcome])
                if self.OPTION_WITH_DESCRIPTION in self._option_list:
                    self.worksheet4.write(
                        self._lineno, level + 1,
                        result_map[job].get(
                            'description',
                            result_map[job].get('summary', "")), self.format15)
                if level:
                    self.worksheet3.set_row(
                        self._lineno, 13, None, {'level': level})
                    if self.OPTION_WITH_DESCRIPTION in self._option_list:
                        self.worksheet4.set_row(
                            self._lineno, 13, None, {'level': level})
                else:
                    self.worksheet3.set_row(self._lineno, 13)
                    if self.OPTION_WITH_DESCRIPTION in self._option_list:
                        self.worksheet4.set_row(self._lineno, 13)
                self._write_job(children, result_map, max_level, level + 1)
            else:
                self.worksheet3.write(
                    self._lineno, max_level + 1, result_map[job]['summary'],
                    self.format08 if self._lineno % 2 else self.format09)
                if self.OPTION_WITH_DESCRIPTION in self._option_list:
                    link_cell = xl_rowcol_to_cell(self._lineno, max_level + 1)
                    self.worksheet3.write_url(
                        self._lineno, max_level + 1,
                        'internal:' + _("Test Descriptions") + '!' + link_cell,
                        self.format08 if self._lineno % 2 else self.format09,
                        result_map[job]['summary'])
                    self.worksheet4.write(
                        self._lineno, max_level + 1,
                        result_map[job]['summary'],
                        self.format08 if self._lineno % 2 else self.format09)
                self.total += 1
                outcome = result_map[job]['outcome']
                self.worksheet3.write(
                    self._lineno, max_level, OMM[outcome].unicode_sigil,
                    self.outcome_format_map[outcome])
                self.worksheet3.write(
                    self._lineno, max_level + 2, OMM[outcome].tr_label,
                    self.outcome_format_map[outcome])
                if outcome == IJobResult.OUTCOME_PASS:
                    self.total_pass += 1
                elif outcome == IJobResult.OUTCOME_FAIL:
                    self.total_fail += 1
                else:
                    # NOTE: this is inaccurate but that's how the original code
                    # behaved. This will be fixed with detailed per-outcome
                    # counters later.
                    self.total_skip += 1
                cert_status = ''
                if 'certification_status' in result_map[job]:
                    cert_status = result_map[job]['certification_status']
                    if cert_status == 'unspecified':
                        cert_status = ''
                self.worksheet3.write(
                    self._lineno, max_level + 3, cert_status,
                    self.format18 if self._lineno % 2 else self.format19)
                io_log = ' '
                if result_map[job]['io_log']:
                    io_log = standard_b64decode(
                        result_map[job]['io_log'].encode()
                    ).decode('UTF-8').rstrip()
                io_lines = len(io_log.splitlines()) - 1
                desc_lines = len(result_map[job].get('description',
                                                     "").splitlines())
                desc_lines -= 1
                self.worksheet3.write(
                    self._lineno, max_level + 4, io_log,
                    self.format16 if self._lineno % 2 else self.format17)
                comments = ' '
                if result_map[job]['comments']:
                    comments = result_map[job]['comments'].rstrip()
                self.worksheet3.write(
                    self._lineno, max_level + 5, comments,
                    self.format16 if self._lineno % 2 else self.format17)
                if self.OPTION_WITH_DESCRIPTION in self._option_list:
                    self.worksheet4.write(
                        self._lineno, max_level + 2,
                        result_map[job].get('description', ""),
                        self.format16 if self._lineno % 2 else self.format17)
                if level:
                    self.worksheet3.set_row(
                        self._lineno, 12 + 10.5 * io_lines,
                        None, {'level': level})
                    if self.OPTION_WITH_DESCRIPTION in self._option_list:
                        self.worksheet4.set_row(
                            self._lineno, 12 + 10.5 * desc_lines,
                            None, {'level': level})
                else:
                    self.worksheet3.set_row(self._lineno, 12 + 10.5 * io_lines)
                    if self.OPTION_WITH_DESCRIPTION in self._option_list:
                        self.worksheet4.set_row(
                            self._lineno, 12 + 10.5 * desc_lines)

    def write_results(self, data):
        if self.OPTION_WITH_UNIT_CATEGORIES in self._option_list:
            tree, max_level = self._tree(
                data['result_map'], data['category_map'])
        else:
            tree, max_level = self._legacy_tree(data['result_map'])
        self.worksheet3.write(3, 1, _('Tests Performed'), self.format03)
        self.worksheet3.freeze_panes(6, 0)
        self.worksheet3.set_tab_color('#DC4C00')  # Orange
        self.worksheet3.set_column(0, 0, 5)
        [self.worksheet3.set_column(i, i, 2) for i in range(1, max_level + 1)]
        self.worksheet3.set_column(max_level + 1, max_level + 1, 48)
        self.worksheet3.set_column(max_level + 2, max_level + 2, 12)
        self.worksheet3.set_column(max_level + 3, max_level + 3, 18)
        self.worksheet3.set_column(max_level + 4, max_level + 4, 65)
        self.worksheet3.set_column(max_level + 5, max_level + 5, 65)
        self.worksheet3.write_row(
            5, max_level + 1,
            [_('Name'), _('Result'), _('Certification Status'), _('I/O Log'),
             _('Comments')],
            self.format07)
        if self.OPTION_WITH_DESCRIPTION in self._option_list:
            self.worksheet4.write(3, 1, _('Test Descriptions'), self.format03)
            self.worksheet4.freeze_panes(6, 0)
            self.worksheet4.set_column(0, 0, 5)
            [self.worksheet4.set_column(i, i, 2)
                for i in range(1, max_level + 1)]
            self.worksheet4.set_column(max_level + 1, max_level + 1, 48)
            self.worksheet4.set_column(max_level + 2, max_level + 2, 65)
            self.worksheet4.write_row(
                5, max_level + 1, [_('Name'), _('Description')], self.format07
            )
        self._lineno = 5
        self._write_job(tree, data['result_map'], max_level)
        self.worksheet3.autofilter(5, max_level, self._lineno, max_level + 3)

    def write_attachments(self, data):
        self.worksheet5.set_column(0, 0, 5)
        self.worksheet5.set_column(1, 1, 120)
        i = 4
        for name in data['attachment_map']:
            try:
                content = standard_b64decode(
                    data['attachment_map'][name].encode()).decode('UTF-8')
            except UnicodeDecodeError:
                # Skip binary attachments
                continue
            self.worksheet5.write(i, 1, name, self.format03)
            i += 1
            self.worksheet5.set_row(
                i, None, None, {'level': 1, 'hidden': True}
            )
            j = 1
            for line in content.splitlines():
                self.worksheet5.write(j + i, 1, line, self.format13)
                self.worksheet5.set_row(
                    j + i, None, None, {'level': 1, 'hidden': True}
                )
                j += 1
            self.worksheet5.set_row(i + j, None, None, {'collapsed': True})
            i += j + 1  # Insert a newline between attachments

    def dump(self, data, stream):
        """
        Public method to dump the XLSX report to a stream
        """
        self.workbook = Workbook(stream)
        self._set_formats()
        if self.OPTION_WITH_SYSTEM_INFO in self._option_list:
            self.worksheet1 = self.workbook.add_worksheet(_('System Info'))
            self.write_systeminfo(data)
        self.worksheet3 = self.workbook.add_worksheet(_('Test Results'))
        if self.OPTION_WITH_DESCRIPTION in self._option_list:
            self.worksheet4 = self.workbook.add_worksheet(
                _('Test Descriptions'))
        self.write_results(data)
        if self.OPTION_WITH_SUMMARY in self._option_list:
            self.worksheet2 = self.workbook.add_worksheet(_('Summary'))
            self.write_summary(data)
        if self.OPTION_WITH_TEXT_ATTACHMENTS in self._option_list:
            self.worksheet5 = self.workbook.add_worksheet(_('Log Files'))
            self.write_attachments(data)
        for worksheet in self.workbook.worksheets():
            worksheet.outline_settings(True, False, False, True)
            worksheet.hide_gridlines(2)
            worksheet.fit_to_pages(1, 0)
            worksheet.write(1, 1, _('System Testing Report'), self.format01)
            worksheet.set_row(1, 30)
        self.workbook.close()
