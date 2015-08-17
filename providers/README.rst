Plainbox Providers
==================

This directory contains a number of Plainbox Providers. Those providers are
kept here for both historic reasons and some extra simplicity in making changes
that also require synchronized updates to other parts of the greater Checkbox
project (e.g. changes to checkbox-support or to plainbox).

In-Tree Providers
=================

The following providers are kept here, in tree:

``2015.com.canonical.certification:qml-tests/``:

    Tests natively implemented in QML and the Ubuntu SDK libraries. Tests in
    this provider are used by Checkbox on the Ubuntu Phone.
    
``plainbox-provider-checkbox/``:

    Oldest and most varied collection of tests. The tests themselves are used
    by various other providers (they are referenced from their test plans).
    
``plainbox-provider-hwcollect/``:

    The provider that is meant to fuel the needs of ``canonical-hw-collection``
    tool. Currently unused.

``plainbox-provider-piglit/``:

    A small provider, split off from the Checkbox provider, focused on wrapping
    and exposing the ``piglit`` OpenGL testing tool. Jobs from this provider
    are used in some test plans, most notably in CDTS.

``plainbox-provider-resource-generic/``:

    A provider much smaller than checkbox that is aways used alongside with it.
    This provider contains various resource jobs and utility scripts. It is
    used in both on Ubuntu desktop and server environments. 

``plainbox-provider-snappy-ubuntu-core/``:

    A provider that contains new jobs focused on Ubuntu Snappy Core
    environment. As of August 2015 this is an area of active research.

``plainbox-provider-ubuntu-touch/``:

    A provider that contains now jobs focused on Ubuntu Phone environments.
    This provider is shipped, bundled, with Checkbox Touch and is available in
    the Ubuntu Store. 

Out-Of-Tree Providers
=====================

The following providers are kept out of tree, they are referenced here so
that developers can find pointers to some of the code that was here before.


``plainbox-provider-canonical-driver-test-suite``:

    The provider is present on the ``cdts`` project, on Lauchpad, in bzr, in
    the main branch of the project. This provider refers to various jobs in the
    checkbox and piglit providers.

    A handy link to the code is:

    https://code.launchpad.net/~checkbox-ihv-ng/cdts/trunk

``plainbox-provider-certification-client``:

    The provider is present on the
    ``plainbox-provider-canonical-certification`` project, on Launchpad, in
    Git, in the ``master-client`` branch.

    This provider is used by the Canonical Certification team for certification
    of "client" hardware (desktops, laptops, etc.). This provider is mainly a
    list of test plans that refer to the jobs in the checkbox provider.

    A handy link to the code is:

    https://code.launchpad.net/~checkbox-dev/plainbox-provider-canonical-certification/+git/plainbox-provider-canonical-certification/+ref/master-client

``plainbox-provider-certification-server``:

    The provider is present on the
    ``plainbox-provider-canonical-certification`` project, on Launchpad, in
    Git, in the ``master-server`` branch.

    This provider is used by the Canonical Certification team for certification
    of server hardware. This provider is mainly a list of test plans that refer
    to the jobs in the checkbox provider.

    A handy link to the code is:

    https://code.launchpad.net/~checkbox-dev/plainbox-provider-canonical-certification/+git/plainbox-provider-canonical-certification/+ref/master-server
