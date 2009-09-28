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
import os
import posixpath

from checkbox.lib.cache import cache
from checkbox.lib.conversion import string_to_type

from checkbox.properties import Path
from checkbox.registries.filename import FilenameRegistry


def cpuinfo_to_processor(uname, cpuinfo):
    # Default values
    processor = {
        "platform": uname,
        "count": 1,
        "type": uname,
        "model": uname,
        "model_number": "",
        "model_version": "",
        "model_revision": "",
        "cache": 0,
        "bogomips": 0,
        "speed": -1,
        "other": ""}

    # Conversion table
    platform_to_conversion = {
        ("i386", "i486", "i586", "i686", "x86_64",): {
            "type": "vendor_id",
            "model": "model name",
            "model_number": "cpu family",
            "model_version": "model",
            "model_revision": "stepping",
            "cache": "cache size",
            "other": "flags",
            "speed": "cpu mhz"},
        ("alpha", "alphaev6",): {
            "count": "cpus detected",
            "type": "cpu",
            "model": "cpu model",
            "model_number": "cpu variation",
            "model_version": ("system type", "system variation",),
            "model_revision": "cpu revision",
            "other": "platform string",
            "speed": "cycle frequency [Hz]"},
        ("ia64",): {
            "type": "vendor",
            "model": "family",
            "model_version": "archrev",
            "model_revision": "revision",
            "other": "features",
            "speed": "cpu mhz"},
        ("ppc64", "ppc",): {
            "type": "platform",
            "model": "cpu",
            "model_version": "revision",
            "vendor": "machine",
            "speed": "clock"},
        ("sparc64", "sparc",): {
            "count": "ncpus probed",
            "type": "type",
            "model": "cpu",
            "model_version": "type",
            "speed": "bogomips"}}

    processor["count"] = cpuinfo.get("count", 1)
    processor["bogomips"] = int(round(float(cpuinfo.get("bogomips", "0.0"))))
    for platform, conversion in platform_to_conversion.items():
        if uname in platform:
            for pkey, ckey in conversion.items():
                if isinstance(ckey, (list, tuple)):
                    processor[pkey] = "/".join([cpuinfo[k] for k in ckey])
                elif ckey in cpuinfo:
                    processor[pkey] = cpuinfo[ckey]

    # Adjust platform and vendor
    if uname[0] == "i" and uname[-2:] == "86":
        processor["platform"] = "i386"
    elif uname[:5] == "alpha":
        processor["platform"] = "alpha"
    elif uname[:5] == "sparc":
        processor["vendor"] = "sun"

    # Adjust cache
    if processor["cache"]:
        processor["cache"] = string_to_type(processor["cache"])

    # Adjust speed
    try:
        if uname[:5] == "alpha":
            speed = processor["speed"].split()[0]
            processor["speed"] = int(round(float(speed))) / 1000000
        elif uname[:5] == "sparc":
            speed = processor["speed"]
            processor["speed"] = int(round(float(speed))) / 2
        else:
            if uname[:3] == "ppc":
                # String is appended with "mhz"
                speed = processor["speed"][:-3]
            else:
                speed = processor["speed"]
            processor["speed"] = int(round(float(speed)) - 1)
    except ValueError:
        processor["speed"] = -1

    # Adjust count
    try:
        processor["count"] = int(processor["count"])
    except ValueError:
        processor["count"] = 1
    else:
        # There is at least one processor
        if processor["count"] == 0:
            processor["count"] = 1

    return processor


class CpuinfoRegistry(FilenameRegistry):
    """Registry for cpuinfo information.

    Each item contained in this registry consists of the processor number
    as key and the corresponding processor registry as value.
    """

    # Filename where cpuinfo is stored.
    filename = Path(default="/proc/cpuinfo")

    # Filename where maximum frequency is stored.
    frequency_filename = Path(default="/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq")

    def _get_attributes(self):
        count = 0
        attributes = {}
        for block in self.split("\n\n"):
            if not block:
                continue

            count += 1
            if count > 1:
                continue

            for line in block.split("\n"):
                if not line:
                    continue

                key, value = line.split(":")
                key, value = key.strip(), value.strip()

                # Handle bogomips on sparc
                if key.endswith("Bogo"):
                    key = "bogomips"

                attributes[key.lower()] = value

        attributes["count"] = count
        return attributes

    @cache
    def items(self):
        uname = os.uname()[4].lower()
        attributes = self._get_attributes()

        processor = cpuinfo_to_processor(uname, attributes)

        # Check for frequency scaling
        if posixpath.exists(self.frequency_filename):
            speed = open(self.frequency_filename).read().strip()
            processor["speed"] = int(speed) / 1000

        return processor.items()


factory = CpuinfoRegistry
