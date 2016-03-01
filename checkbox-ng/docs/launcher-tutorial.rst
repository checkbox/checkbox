Checkbox/plainbox launchers tutorial
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Checkbox launchers are INI files that customize checkbox experience. The
customization includes:
 * choosing what jobs will be run
 * how to handle machine restart
 * what type of UI to use
 * how to handle the results

Each section in the launcher is optional, when not supplied, the default values
will be used.

This tutorial describes Launchers version 1.

Launcher meta-information
=========================

Launcher meta-information helps to provide consistent checkbox behaviour in the
future.

``[launcher]``

Beginning of the launcher meta-information section.

``app_id``

This fields helps to differentiate between checkbox front-ends. This way
sessions started with launcher with one ``app_id`` won't interfere with
sessions started with a different launcher (provider it has ``app_id`` set to
other value). Default value: ``checkbox-cli``

``app_version``

This field is purely informational.

``launcher_version``

Version of the launcher language syntax and semantics to use.

``api_flags``

API flags variable determines optional feature set.
List of API flags that this launcher requires. Items should be seperated by
spaces or commas. The default value is an empty list.

``api_version``

API version determines the behaviour of the launcher. Each checkbox feature  is
added at a specific API version. Default behaviours don't change silently;
explicit launcher change is required. Default value: ``0.99``

Launcher section example:

::

    [launcher]
    app_id = System testing
    launcher_version = 1

Providers section
=================

This section provides control over which providers are used by the launcher.

``[providers]``

Beginning of the providers section.

``use``

A list of globs, from which a provider id must match at least one in order to
be used. By default all providers are used.

Providers section example:

::

    [providers]
    use = provider1, provider2, provider-*


Test plan section
=================

This section provides control over which test plans are visible in the menus
and optionally forces the app to use particular one.

``[test plan]``

Beginning of the test plan section.

``unit``

An ID of a test plan that should be selected by default. By default nothing is
selected.

``filter``

Glob that test plan IDs have to match in order to be visible. Default value:
``*``

``forced``

If set to ``yes``, test plan selection screen will be skipped. Requires
``unit`` field to be set. Default value: ``no``.


Test selection section
======================
This section provides lets forcing of test selection.

``[test selection]``

Beginning of the test selection section

``forced``

If set to ``yes``, test selection screen will be skipped and all test specified
in the test plan will be selected. Default value: ``no``

User Interface section
======================

This section controls which type of UI to use.

``[ui]``

Beginning of the user interface section

``type``

Type of UI to use. This has to be set to ``interactive`` or to ``silent``.
Default value: ``interactive``.
Note: using ``silent`` UI type requires forcing test selection and test plan
selection.

Restart section
===============

This section enables fine control over how checkbox is restarted.

``[restart]``

Beginning of the restart section

``strategy``

Override the restart strategy that should be used. Currently supported
strategies are ``XDG`` and ``Snappy``. By default the best strategy is
determined in runtime.


Generating reports
==================

Creation of reports is govern by three sections: ``report``, ``exporter``, and
``transport``. Each of those sections might be specified multiple times to
provide more than one report.

Exporter
--------

``[exporter:exporter_name]``

Beginning of an exporter declaration. Note that ``exporter_name`` should be
replaced with something meaningful, like ``html``.

``unit``

ID of an exporter to use. To get the list of available exporter in your system
run ``$ plainbox dev list exporter``.

``options``

A list of options that will be supplied to the exporter. Items should be seperated by
spaces or commas.

Example:

::

    [exporter:html]
    unit = 2013.com.canonical.plainbox::html

Transport
---------

``[transport:transport_name]``
Beginning of a transport declaration. Note that ``transport_name`` should be
replaced with something meaningful, like ``standard_out``.

``type``

Type of a transport to use. Allowed values are: ``stream``, ``file``, and
``certification``.

Depending on the type of transport there might be additional fields.


+-------------------+---------------+----------------+----------------------+
| transport type    |  variables    | meaning        | example              |
+===================+===============+================+======================+
| ``stream``        | ``stream``    | which stream to| ``[transport:out]``  |
|                   |               | use ``stdout`` |                      |
|                   |               | or ``stderr``  | ``type = stream``    |
|                   |               |                |                      |
|                   |               |                | ``stream = stdout``  |
+-------------------+---------------+----------------+----------------------+
| ``file``          | ``path``      | where to save  | ``[transport:f1]``   |
|                   |               | the file       |                      |
|                   |               |                | ``type = file``      |
|                   |               |                |                      |
|                   |               |                | ``path = ~/report``  |
+-------------------+---------------+----------------+----------------------+
| ``certification`` | ``secure-id`` | secure-id to   | ``[transport:c3]``   |
|                   |               | use when       |                      |
|                   |               | uploading to   | ``secure_id = 01``\  |
|                   |               | certification  | ``23456789ABCD``     |
|                   |               | sites          |                      |
|                   |               |                | ``staging = yes``    |
|                   |               |                |                      |
|                   +---------------+----------------+                      |
|                   | ``staging``   | determines if  |                      |
|                   |               | staging site   |                      |
|                   |               | should be used |                      |
|                   |               | Default:       |                      |
|                   |               | ``no``         |                      |
|                   |               |                |                      |
|                   |               |                |                      |
|                   |               |                |                      |
+-------------------+---------------+----------------+----------------------+


Report
------

``[report:report_name]``

Beginning of a report  declaration. Note that ``report_name`` should be
replaced with something meaningful, like ``to_screen``.

``exporter``

Name of the exporter to use

``transport``

Name of the transport to use

``forced``

If set to ``yes`` will make checkbox always produce the report (skipping the
prompt). Default value: ``no``.

Example of all three sections working to produce a report:

::

    [exporter:text]
    unit = 2013.com.canonical.plainbox::text

    [transport:out]
    type = stream
    stream = stdout

    [report:screen]
    exporter = text
    transport = out
    forced = yes


Launcher examples
=================

1) Fully automatic run of all tests from
'2013.com.canonical.certification::smoke' test plan concluded by producing text
report to standard output.

::

    #!/usr/bin/env checkbox-cli

    [launcher]
    launcher_version = 1
    app_id = Smoke tester

    [test plan]
    unit = 2013.com.canonical.certification::smoke
    forced = yes

    [test selection]
    forced = yes

    [ui]
    type = silent

    [transport:out]
    type = stream
    stream = stdout

    [exporter:text]
    unit = 2013.com.canonical.plainbox::text

    [report:screen]
    transport = outfile
    exporter = text

2) Interactive testing of FooBar project. Report should be uploaded to the
staging version of certification site and saved to /tmp/submission.xml

::

    #!/usr/bin/env checkbox-cli

    [launcher]
    launcher_version = 1
    app_id = FooBar testing

    [providers]
    use = 2016.com.megacorp.foo::bar*

    [test plan]
    unit = 2016.com.megacorp.foo::bar-generic

    [ui]
    type = silent

    [transport:certification]
    type = certification
    secure-id = 00112233445566
    staging = yes

    [transport:local_file]
    type = file
    path = /tmp/submission.xml

    [exporter:xml]
    unit = 2013.com.canonical.plainbox::hexr

    [report:c3-staging]
    transport = outfile
    exporter = xml

    [report:file]
    transport = local_file
    exporter = xml
