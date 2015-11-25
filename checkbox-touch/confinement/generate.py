#!/usr/bin/env python3
# This file is part of Checkbox.
#
# Copyright 2015 Canonical Ltd.
# Written by:
#   Maciej Kisielewski <maciej.kisielewski@canonical.com>
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
import argparse
import os
import string
import sys


CONTENT_HUB = """{
    "destination": [ "documents"],
    "source": [ "documents"],
    "share": [ "documents"]
}"""

APPARMOR = """{
    "policy_groups": [
        "networking",
        "webview",
        "content_exchange",
        "content_exchange_source"
    ],
    "policy_version": 1.2
}"""


DESKTOP = """[Desktop Entry]
Name=Checkbox-${partial_id}
Comment=${partial_id} - confined test from Checkbox
Exec=qmlscene -I lib/py/plainbox/data/plainbox-qml-modules/ -I providers/${provider_name}/data/ --checkbox-name=${full_checkbox_name} --job ../providers/${provider_name}/data/${qml_file} $$@ confinement/plainbox-confined-shell.qml
Icon=checkbox-touch.svg
Terminal=false
Type=Application
X-Ubuntu-Touch=true
"""

HOOK = """
"${partial_id}": {
      "apparmor": "providers/${provider_name}/data/confined/${partial_id}.apparmor",
      "desktop": "providers/${provider_name}/data/confined/${partial_id}.desktop",
      "content-hub": "providers/${provider_name}/data/confined/${partial_id}-ch.json"
}
"""

def generate_confinement(provider_name, partial_id, full_checkbox_name, qml_file):
    # generate content-hub file
    target_dir = os.path.join('data', 'confined')
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    content_hub_path = os.path.join(target_dir, partial_id + '-ch.json')
    with open(content_hub_path, "wt") as f:
        f.write(CONTENT_HUB)

    # generate apparmor file
    apparmor_path = os.path.join(target_dir, partial_id + '.apparmor')
    with open(apparmor_path, "wt") as f:
        f.write(APPARMOR)

 
    # generate desktop file
    desktop_path = os.path.join(target_dir, partial_id + '.desktop')
    template = string.Template(DESKTOP)
    with open(desktop_path, "wt") as f:
        f.write(template.substitute(partial_id=partial_id, provider_name=provider_name, full_checkbox_name=full_checkbox_name, qml_file=qml_file))
    return string.Template(HOOK).substitute(
        provider_name=provider_name, partial_id=partial_id)



def main():
    parser = argparse.ArgumentParser(
        description="Generate confinement files for Checkbox")
    parser.add_argument('--checkbox_version', action='store', type=str)
    parser.add_argument('job_ids', nargs='+')
    args = parser.parse_args()
    checkbox_name = "com.ubuntu.checkbox_checkbox-touch_" + args.checkbox_version

    # check if current dir looks like a provider - very dumb heuristic
    if not os.path.exists('manage.py'):
        sys.exit("Current directory doesn't look like a plainbox provider")
    provider_name = os.path.split(os.getcwd())[-1]

    hooks = ''
    for job in args.job_ids:
        hooks += generate_confinement(provider_name, job, checkbox_name, job + '.qml')

    print("Add following hooks to your checkbox-touch.manifest:")
    print(hooks)


if __name__ == '__main__':
    main()
