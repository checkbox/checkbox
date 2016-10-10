The Checkbox Project
====================

This document serves as a roadmap to the curious folk that want to know how to
make in-and-outs of the various files living here.

The checkbox project was actually a collection of smaller projects, all living
in one big bzr repository (for several technical and historical reasons).

You can still find the old content of the legacy lp:checkbox trunk in the the
MIGRATED2GIT directory.

But remember that the bzr repository is no longer the active home of the
following projects. They all have their own git repositories.

checkbox-converged
------------------

An Ubuntu SDK application (Python + QML) with a modern touch interface,
optimized for phablet devices.

- lp:checkbox-converged

checkbox-ng
-----------

A python3 console application (checkbox-cli). This is also the command-line
launcher interpreter used in many providers.

This project depends on plainbox (for all of the core logic) and on a number of
test providers.

- lp:checkbox-ng

checkbox-support
----------------

A python3 library that contains support code for various providers inherited
from checkbox-old (now removed). This is a dependency of many (but not all)
providers that are in providers/

- lp:checkbox-support

plainbox
--------

A python3 library that contains the core logic of testing applications such as
checkbox. Also a collection of development tools for test authors.

- lp:plainbox

providers (conversion to Git in progress)
-----------------------------------------

A directory with various provider definitions. Have a look at a particular
provider for details. This is where actual valuable tests are. There are many
providers as they have different goals and/or dependencies. Some providers
depend on a base provider for shared job definitions.

Converted providers (Week42 2016):

- lp:plainbox-provider-resource
- lp:plainbox-provider-checkbox
- lp:plainbox-provider-certification-client
- lp:plainbox-provider-certification-server

support
-------

Support code for the project that is never released, for testing, development,
CI loops, etc.

- https://code.launchpad.net/~checkbox-dev/checkbox/+git/support

cep
---

All of Checkbox Enhancement Proposal documents. All bigger changes to the stack
have an associated document that explains the change, its implementation and
impact.

- https://code.launchpad.net/~checkbox-dev/checkbox/+git/cep
