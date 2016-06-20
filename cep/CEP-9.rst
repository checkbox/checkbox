===================================================
Checkbox Enhancement Proposal 9: Confined QML jobs
===================================================

Summary
=======

This CEP defines 'confined' flag for qml-native jobs that makes
checkbox-converged run them as separate apps.

Rationale
=========

Currently when qml-jobs are run by checkbox-converged, they are run with the
same apparmor profile as checkbox-converged. For some tests we want to change
the security profile the test will run in. This CEP proposes a new way of
running qml-native jobs in which the policies are changed.


Example
=======

We need to provide a test that checks if the device asks for permission, when
an app asks for location data. Let's call it "the Test"
This job cannot be an ordinary qml-job, as apparmor policy defined for
checkbox-converged would be used to carry the test out.

Expected behaviour when running tests is as follows:
- checkbox-converged gets to the Test
- device runs the Test with different set of policies
- prompt asking whether to let the Test use location information
- testing concludes
- checkbox-converged switches to the next test

Changing apparmor policies
===========================

Confined tests will have additional syntax in their definition to allow
user-defined policy.
Flag ``confined`` will be used, to inform that the test should run in a
confined manner.
This field - ``apparmor`` - will point to the file that
should be used as apparmor profile. Should this file be missing, the test will
have no privileges and will run fully confined.

Impact
======

Adding confined tests requires change in how providers are handled by
Checkbox-Converged. Instead of copying them as-is, they need to be built. This
*does not* require any change to existing providers and *does not* change
behaviour of the app.
For other Checkbox Applications (cli, gui), confined tests will be executed as
ordinary qml-native jobs, because apparmor policies don't affect platforms
that those front-ends run on.

Implementation
==============

Proposed flow
-------------
Checkbox-Converged launches an app containing the test and holds its execution.
Device switches to running the test-app. ::

- Test is performed.
- Test-app prepares test result object.
- Test-app pushes result object to ContentHub with Checkbox-Converged as the
- destination requesting immediate consumption.
- Test-app terminates.
- Device switches back to Checkbox-Converged and processes the result object.
- Checkbox-Converged carries on with normal execution.

Multi-app
---------
Current architecture of click bundles lets us to bundle multiple apps in one
click. Every app may have different apparmor policy so the easiest way is to
provide means for checkbox-converged to be delivered with all confined tests
packaged as seperate apps within the same click package. Proof of concept of
that is here: https://code.launchpad.net/~kissiel/+git/multi-app/+ref/master


Generating apps
---------------
The sandboxed test needs to communicate its result back to checkbox-converged;
to achieve this goal Content Hub can be used. Normally the communication
initiator (confined test) would have to ask user to pick the app which they
would like to send the results to. This can be avoided by hardcoding qualified
name of the destination. This qualified name requires precise information about
current version of Checkbox-Converged. To make this part reliable, information
about consumer and sender must be generated during creation of the click
package.  The whole process can be governed by the ``build`` command of
``manage.py`` script of the provider. Building a provider that has confined
test would mean generating those applications and generating hook entry for the
'global' click manifest to contain.


Job definition examples
=======================
::

    id: normal-qml-job
    _summary: A QML job that runs with the default apparmor settings
    plugin: qml
    qml_file: foo.qml
    flags: preserve-locale
    estimated_duration: 10

    id: confied-qml-job
    _summary: A QML job that is fully confined
    plugin: qml
    qml_file: bar.qml
    flags: confined preserve-locale
    estimated_duration: 10

    id: custom-confinement-qml-job
    _summary: A QML job that is run using custom apparmor settings
    plugin: qml
    qml_file: baz.qml
    flags: confined preserve-locale
    apparmor: baz_apparmor.json
    estimated_duration: 10
