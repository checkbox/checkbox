The Checkbox Project
====================

This document serves as a roadmap to the curious folk that want to know how to
make in-and-outs of the various files living here.

The checkbox project is actually a collection of smaller projects, all living
in one big repository (for several technical and historical reasons). The
top-level directory as at least the following components (in alphabetical
order).

checkbox-gui
------------

An Ubuntu SDK application (C++/QML) with a modern touch interface for testing.
No actual test definitions exist there.

This project depends on the checkbox-ng project (for the DBus API) and on a
number of test providers (that all live or shall live in the providers/
top-level directory)

checkbox-ng
-----------

A python3 console application that contains a number of executables (most
notably checkbox and a collection of derivative canonical-\* executables) that
run a part of checkbox-ng.

This project depends on plainbox (for all of the core logic) and on a number of
test providers, similarly to checkbox-gui.

checkbox-support
----------------

A python3 library that contains support code for various providers inherited
from checkbox-old (now removed). This is a dependency of many (but not all)
providers that are in providers/

plainbox-client
---------------

Unfinished python3 interface for the DBus API implemented in checkbox-ng. May
go away, may become important and mature. We'll see. It only depends on python3
and python3-gi (for GDBus).

plainbox
--------

A python3 library that contains the core logic of testing applications such as
checkbox. Also a collection of development tools for test authors.

providers
---------

A directory with various provider definitions. Have a look at a particular
provider for details. This is where actual valuable tests are. There are many
providers as they have different goals and/or dependencies. Some providers
depend on a base provider for shared job definitions.

support
-------

Support code for the project that is never released, for testing, development,
CI loops, etc.
