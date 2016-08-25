.. _tutorials:

Checkbox tutorials
==================

Creating an empty provider
--------------------------

Plainbox Providers are bundles containing information how to run tests.

To create an empty provider run::

   $ plainbox startprovider --empty 2016.com.example:myprovider

``plainbox`` is the internal tool of checkbox. It's used on rare occasions,
like creating a new provider.  ``--empty`` informs plainbox that you want to
start from scratch. ``2016.com.example:myprovider`` is the name of the provider.
Providers use IQN naming, it helps in tracking down ownership of the provider.

Plainbox Jobs are the things that describe how tests are run. Those Jobs are
defined in .pxu files, in 'units' directory of the provider.

The provider we've just created doesn't have that directory, let's create it::

    $ cd 2016.com.example\:myprovider
    $ mkdir units

Adding a simple job to a provider
---------------------------------

Jobs loosely follow RFC822 syntax. I.e. most content follow ``key:value``
pattern.

Let's add a simple job that runs a command.

Open any ``.pxu`` file in ``units`` directory of the provider
(if there isn't any, just create one, like ``units.pxu``).
And add following content::
    
    id: my-first-job
    flags: simple
    command: mycommand
    
``id`` is used for identification purposes
``flags`` enables extra features. In the case of ``simple``, it lets us not
specify all the typical fields - Checkbox will infer some values for us.
``command`` specifies which command to run. Here it's ``mycommand``

In order for jobs to be visible in Checkbox they have to be included in some
test plan. Let's add a test plan definition to the same ``.pxu`` file.::

    unit: test plan
    id: first-tp
    name: My first test plan
    include: my-first-job

.. warning::
    Separated entities in the .pxu file has to be separated by at least one
    empty line.


Running jobs from a newly created provider
------------------------------------------

In order for Checkbox to `see` the provider we have to install it.
To do so run::

    $ sudo ./manage.py install

Now we're ready to launch Checkbox! Start the command line version with::

    $ checkbox-cli

Follow the instructions on the screen. The test will (probably) fail, because 
of ``mycommand`` missing in your system. Let's change the job definition to do
something meaningful instead. Open ``units.pxu``, and change the line::

    command: mycommand

to ::

    command: [ `df -B 1G --output=avail $HOME |tail -n1` -gt 10 ]

.. note::
    This command checks if there's at least 10GB of free space in $HOME

This change won't be available just yet, as we still have an old version of the
provider installed in the system. Let's remove the previous version, and
install the new one.::

    $ sudo rm -rf /usr/local/lib/plainbox-providers-1/2016.com.example\:myprovider/
    $ sudo ./manage.py install

This sudo operations (hopefully) look dangerous to you. See next part to see
how to avoid that.

Developing provider without constantly reinstalling it
------------------------------------------------------

Instead of reinstalling the provider every time you change anything in it, you
can make Checkbox read it directly from the place you're changing it in.::

    $ ./manage.py develop

Because now Checkbox may see two instances of the same provider, make sure you
remove the previous one.

.. note::
    ``./manage.py`` develop doesn't require sudo, as it makes all the
    references in user's home.

Improving job definition
------------------------

When you run Checkbox you see the job displayed as 'my-first-job' which is the
id of the job, which is not very human-friendly. This is because of the
``simple`` flag. Let's improve our Job definition. Open ``units.pxu`` and
replace the job definition with::

    id: my-first-job
    _summary: 10GB available in $HOME
    _description:
        this test checks if there's at least 10gb of free space in user's home
        directory
    plugin: shell
    estimated_duration: 0.01
    command: [ `df -B 1G --output=avail $HOME |tail -n1` -gt 10 ]

New stuff::

    _summary: 10GB available in $HOME

Summary is shown in Checkbox screens where jobs are selected. It's a
human-friendly identification of the job. It should should be short (50 - 70
chars), as it's printed in one line. ``_`` means at the beginning means
the field is translatable.

::

    _purpose:
        this test checks if there's at least 10gb of free space in user's home
        directory

Purpose as the name suggest should describe the purpose of the test. 


::

    plugin: shell

Plugin tells Checkbox what kind of job is it. ``shell`` means it's a automated
test that runs a command and uses it's return code to determine jobs outcome.

::

    estimated_duration: 0.01

Tells Checkbox how long the test is expected to run. This field is currently
informative only.

