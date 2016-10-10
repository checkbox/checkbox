#!/bin/bash

set -e

mkdir -p ${1:-"checkbox-project"} && cd ${1:-"checkbox-project"}
git clone git+ssh://git.launchpad.net/~checkbox-dev/checkbox/+git/support
git clone git+ssh://git.launchpad.net/plainbox
git clone git+ssh://git.launchpad.net/checkbox-ng
git clone git+ssh://git.launchpad.net/checkbox-support
git clone git+ssh://git.launchpad.net/checkbox-converged
git clone git+ssh://git.launchpad.net/plainbox-provider-resource providers/plainbox-provider-resource
git clone git+ssh://git.launchpad.net/plainbox-provider-checkbox providers/plainbox-provider-checkbox
git clone git+ssh://git.launchpad.net/plainbox-provider-certification-client providers/plainbox-provider-certification-client
git clone git+ssh://git.launchpad.net/plainbox-provider-certification-server providers/plainbox-provider-certification-server
git clone git+ssh://git.launchpad.net/plainbox-provider-ubuntu-touch providers/plainbox-provider-ubuntu-touch
ln -s support/mk-venv mk-venv
