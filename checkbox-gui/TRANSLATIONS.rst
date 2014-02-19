Updating translations
=====================

Translations for Checkbox GUI happen in `Launchpad Translations
<https://translations.launchpad.net/checkbox>`_ and
are automatically committed daily on the trunk branch in the po/ folder.

They are then built and installed as part of the package build, so that
developers don't really need to worry about them.

However, there is one task that needs to be taken care of: exposing new
translatable messages to translators. So whenever you add new translatable
messages in the code, make sure to follow these steps::

    cd po
    make pot

Then commit the updated .pot file with the rest of your merge request. Once
the branch lands Launchpad should take care of all the rest!

Behind the scenes
=================

Behind the scenes, whenever the .pot file (also known as translations template)
is committed to trunk Launchpad reads it and updates the translatable strings
exposed in the web UI. This will enable translators to work on the new strings.
The translations template contains all translatable strings that have been
extracted from the source code files.

Launchpad will then store translations in its database and will commit them daily
in the form of textual .po files to trunk. The PO files are also usually
referred to as the translations files. You'll find a translation file for each
language the app has got at least a translated message available for.

Translations follow the standard `gettext format
<https://www.gnu.org/software/gettext>`_.
