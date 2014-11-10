# This file is part of Checkbox.
#
# Copyright 2013 Canonical Ltd.
# Written by:
#   Zygmunt Krynicki <zygmunt.krynicki@canonical.com>
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

"""
:mod:`plainbox.impl.secure.providers.v1` -- Implementation of V1 provider
=========================================================================
"""
import abc
import errno
import gettext
import logging
import os

from plainbox.abc import IProvider1, IProviderBackend1
from plainbox.i18n import gettext as _
from plainbox.impl.secure.config import Config, Variable
from plainbox.impl.secure.config import IValidator
from plainbox.impl.secure.config import NotEmptyValidator
from plainbox.impl.secure.config import NotUnsetValidator
from plainbox.impl.secure.config import PatternValidator
from plainbox.impl.secure.config import Unset
from plainbox.impl.secure.origin import Origin
from plainbox.impl.secure.plugins import FsPlugInCollection
from plainbox.impl.secure.plugins import IPlugIn
from plainbox.impl.secure.plugins import PlugInError
from plainbox.impl.secure.plugins import now
from plainbox.impl.secure.qualifiers import WhiteList
from plainbox.impl.secure.rfc822 import FileTextSource
from plainbox.impl.secure.rfc822 import load_rfc822_records
from plainbox.impl.secure.rfc822 import RFC822SyntaxError
from plainbox.impl.unit import all_units
from plainbox.impl.unit.file import FileRole
from plainbox.impl.unit.file import FileUnit
from plainbox.impl.unit.testplan import TestPlanUnit
from plainbox.impl.validation import Severity
from plainbox.impl.validation import ValidationError


logger = logging.getLogger("plainbox.secure.providers.v1")


class IVirtualUnitSynthethizer(metaclass=abc.ABCMeta):
    """
    Interface for all virtual unit synthetizers

    Classes implementing this interface synthetise virtual units while loading
    some other objects (possibly units), for maintaining backwards
    compatibility
    """

    @abc.abstractmethod
    def synthetize_virtual_units(self, filename, text, provider):
        """
        Synthethise virtual units

        :param filename:
            Name of the file with unit definitions
        :param text:
            Full text of the the file pointed to by ``filename``
        :param provider:
            A provider object to which those units belong to

        This method is called automatically by :meth:`__init__()` to create
        and add additional, virtual units, based on the file that was loaded.
        """


class WhiteListPlugIn(IPlugIn, IVirtualUnitSynthethizer):
    """
    A specialized :class:`plainbox.impl.secure.plugins.IPlugIn` that loads
    :class:`plainbox.impl.secure.qualifiers.WhiteList` instances from a file.
    """

    def __init__(self, filename, text, load_time, provider=None):
        """
        Initialize the plug-in with the specified name text

        :param filename:
            Name of the file that the plugin was loaded from
        :param text:
            Full text of the loaded file
        :param provider:
            An (optional) provider object. This parameter is highly
            recommended. If supplied, it associates the whitelist (as well as
            the synthetized virtual test plan unit) with the namespace and i18n
            resources of the specified provider).
        """
        self._whitelist = None
        self._unit_list = []
        self._load_time = load_time
        self._wrap_time = 0
        start_time = now()
        try:
            self._whitelist = WhiteList.from_string(
                text, filename=filename,
                implicit_namespace=(
                    provider.namespace
                    if provider is not None else None))
        except Exception as exc:
            raise PlugInError(
                _("Cannot load whitelist {!r}: {}").format(filename, exc))
        else:
            self.synthetize_virtual_units(filename, text, provider)
        self._wrap_time = now() - start_time

    @property
    def plugin_name(self):
        """
        plugin name, the name of the WhiteList
        """
        return self._whitelist.name

    @property
    def plugin_object(self):
        """
        plugin object, the actual WhiteList instance
        """
        return self._whitelist

    @property
    def plugin_load_time(self) -> float:
        """
        time, in fractional seconds, that was needed to load the plugin
        """
        return self._load_time

    @property
    def plugin_wrap_time(self) -> float:
        """
        time, in fractional seconds, that was needed to wrap the plugin

        .. note::
            The difference between ``plugin_wrap_time`` and
            ``plugin_load_time`` depends on context. In practical terms the sum
            of the two is interesting for analysis but in some cases having
            access to both may be important.
        """
        return self._wrap_time

    @property
    def unit_list(self):
        """
        list of loaded units

        ..note::
            This property is not a part of the standard API of IPlugIn
        """
        return self._unit_list

    def synthetize_virtual_units(self, filename, text, provider):
        """
        Synthethise virtual units

        :param filename:
            Name of the file with unit definitions
        :param text:
            Full text of the the file pointed to by ``filename``
        :param provider:
            A provider object to which those units belong to

        This method is called automatically by :meth:`__init__()` to create
        and add additional, virtual units, based on the file that was loaded.

        This implementation instantiates a :class:`FileUnit` with
        role :attr:`FileRole.legacy_whitelist` and a :class:`TestPlanUnit`
        corresponding to the whitelist data.
        """
        self._unit_list.append(self._make_file_unit(filename, provider))
        self._unit_list.append(self._make_test_plan_unit(
            filename, text, provider))

    def _make_file_unit(self, filename, provider):
        return FileUnit({
            'unit': FileUnit.Meta.name,
            'path': filename,
            'role': FileRole.legacy_whitelist,
        }, origin=Origin(FileTextSource(filename)), provider=provider,
        virtual=True)

    def _make_test_plan_unit(self, filename, text, provider):
        name = os.path.basename(os.path.splitext(filename)[0])
        origin = Origin(FileTextSource(filename), 1, text.count('\n'))
        field_offset_map = {'include': 0}
        return TestPlanUnit({
            'unit': TestPlanUnit.Meta.name,
            'id': name,
            'name': name,
            'include': text,
        }, origin=origin, provider=provider, field_offset_map=field_offset_map,
        virtual=True)


class UnitPlugIn(IPlugIn, IVirtualUnitSynthethizer):
    """
    A specialized :class:`plainbox.impl.secure.plugins.IPlugIn` that loads a
    list of :class:`plainbox.impl.unit.Unit` instances from a file.
    """

    @staticmethod
    def _get_unit_cls(unit_name):
        """
        Get a class that implements the specified unit
        """
        all_units.load()
        return all_units.get_by_name(unit_name).plugin_object

    def __init__(self, filename, text, load_time, provider, *,
                 validate=True, validation_kwargs=None,
                 check=False, context=None):
        """
        Initialize the plug-in with the specified name text

        :param filename:
            Name of the file with unit definitions
        :param text:
            Full text of the file with unit definitions
        :param provider:
            A provider object to which those units belong to
        :param validate:
            Enable unit validation. Incorrect unit definitions will not be
            loaded and will abort the process of loading of the remainder of
            the jobs.  This is ON by default to prevent broken units from being
            used. This is a keyword-only argument.
        :param validation_kwargs:
            Keyword arguments to pass to the Unit.validate().  Note, this is a
            single argument. This is a keyword-only argument.
        :param check:
            Enable unit checking. Incorrect unit definitions will not be loaded
            and will abort the process of loading of the remainder of the jobs.
            This is OFF by default to prevent broken units from being used.
            This is a keyword-only argument.
        :param context:
            If checking, use this validation context.
        """
        self._filename = filename
        self._unit_list = []
        self._load_time = load_time
        self._wrap_time = 0
        start_time = now()
        if validation_kwargs is None:
            validation_kwargs = {}
        logger.debug(_("Loading units from %r..."), filename)
        try:
            records = load_rfc822_records(
                text, source=FileTextSource(filename))
        except RFC822SyntaxError as exc:
            raise PlugInError(
                _("Cannot load job definitions from {!r}: {}").format(
                    filename, exc))
        for record in records:
            unit_name = record.data.get('unit', 'job')
            try:
                unit_cls = self._get_unit_cls(unit_name)
            except KeyError:
                raise PlugInError(
                    _("Unknown unit type: {!r}").format(unit_name))
            try:
                unit = unit_cls.from_rfc822_record(record, provider)
            except ValueError as exc:
                raise PlugInError(
                    _("Cannot define unit from record {!r}: {}").format(
                        record, exc))
            if check:
                for issue in unit.check(context=context, live=True):
                    if issue.severity is Severity.error:
                        raise PlugInError(
                            _("Problem in unit definition, {}").format(issue))
            if validate:
                try:
                    unit.validate(**validation_kwargs)
                except ValidationError as exc:
                    raise PlugInError(
                        _("Problem in unit definition, field {}: {}").format(
                            exc.field, exc.problem))
            self._unit_list.append(unit)
            logger.debug(_("Loaded %r"), unit)
        self.synthetize_virtual_units(filename, text, provider)
        self._wrap_time = now() - start_time

    def synthetize_virtual_units(self, filename, text, provider):
        """
        Synthethise virtual units

        :param filename:
            Name of the file with unit definitions
        :param text:
            Full text of the the file pointed to by ``filename``
        :param provider:
            A provider object to which those units belong to

        This method is called automatically by :meth:`__init__()` to create
        and add additional, virtual units, based on the file that was loaded.

        This implementation instantiates only one FileUnit() with
        role :attr:`FileRole.unit_source`
        """
        self._unit_list.append(self._make_file_unit(filename, provider))

    def _make_file_unit(self, filename, provider):
        return FileUnit({
            'unit': FileUnit.Meta.name,
            'path': filename,
            'role': FileRole.unit_source,
        }, origin=Origin(FileTextSource(filename)), provider=provider)

    @property
    def plugin_name(self):
        """
        plugin name, name of the file we loaded units from
        """
        return self._filename

    @property
    def plugin_object(self):
        """
        plugin object, a list of Unit instances
        """
        return self._unit_list

    @property
    def plugin_load_time(self) -> float:
        """
        time, in fractional seconds, that was needed to load the plugin
        """
        return self._load_time

    @property
    def plugin_wrap_time(self) -> float:
        """
        time, in fractional seconds, that was needed to wrap the plugin

        .. note::
            The difference between ``plugin_wrap_time`` and
            ``plugin_load_time`` depends on context. In practical terms the sum
            of the two is interesting for analysis but in some cases having
            access to both may be important.
        """
        return self._wrap_time


class Provider1(IProvider1, IProviderBackend1):
    """
    A v1 provider implementation.

    A provider is a container of jobs and whitelists. It provides additional
    meta-data and knows about location of essential directories to both load
    structured data and provide runtime information for job execution.

    Providers are normally loaded with :class:`Provider1PlugIn`, due to the
    number of fields involved in basic initialization.
    """

    def __init__(self, name, version, description, secure, gettext_domain,
                 units_dir, jobs_dir, whitelists_dir, data_dir, bin_dir,
                 locale_dir, base_dir, *, validate=True,
                 validation_kwargs=None, check=False, context=None):
        """
        Initialize a provider with a set of meta-data and directories.

        :param name:
            provider name / ID

        :param version:
            provider version

        :param description:
            provider version

            This is the untranslated version of this field. Implementations may
            obtain the localized version based on the gettext_domain property.

        :param secure:
            secure bit

            When True jobs from this provider should be available via the
            trusted launcher mechanism. It should be set to True for
            system-wide installed providers.

        :param gettext_domain:
            gettext domain that contains translations for this provider

        :param units_dir:
            path of the directory with unit definitions

        :param jobs_dir:
            path of the directory with job definitions

        :param whitelists_dir:
            path of the directory with whitelists definitions (aka test-plans)

        :param data_dir:
            path of the directory with files used by jobs at runtime

        :param bin_dir:
            path of the directory with additional executables

        :param locale_dir:
            path of the directory with locale database (translation catalogs)

        :param base_dir:
            path of the directory with (perhaps) all of jobs_dir,
            whitelist_dir, data_dir, bin_dir, locale_dir. This may be None.
            This is also the effective value of $CHECKBOX_SHARE

        :param validate:
            Enable job validation. Incorrect job definitions will not be loaded
            and will abort the process of loading of the remainder of the jobs.
            This is ON by default to prevent broken job definitions from being
            used. This is a keyword-only argument.

        :param validation_kwargs:
            Keyword arguments to pass to the JobDefinition.validate().  Note,
            this is a single argument. This is a keyword-only argument.
        """
        # Meta-data
        self._name = name
        self._version = version
        self._description = description
        self._secure = secure
        self._gettext_domain = gettext_domain
        # Directories
        self._units_dir = units_dir
        self._jobs_dir = jobs_dir
        self._whitelists_dir = whitelists_dir
        self._data_dir = data_dir
        self._bin_dir = bin_dir
        self._locale_dir = locale_dir
        self._base_dir = base_dir
        # Load and setup everything
        self._load_whitelists()
        self._load_units(validate, validation_kwargs, check, context)
        self._setup_translations()

    def _load_whitelists(self):
        if self.whitelists_dir is not None:
            whitelists_dir_list = [self.whitelists_dir]
        else:
            whitelists_dir_list = []
        self._whitelist_collection = FsPlugInCollection(
            whitelists_dir_list, ext=".whitelist", wrapper=WhiteListPlugIn,
            provider=self)

    def _load_units(self, validate, validation_kwargs, check, context):
        units_dir_list = []
        if self.jobs_dir is not None:
            units_dir_list.append(self.jobs_dir)
        if self.units_dir is not None:
            units_dir_list.append(self.units_dir)
        self._unit_collection = FsPlugInCollection(
            units_dir_list, ext=(".txt", ".txt.in", ".pxu"), recursive=True,
            wrapper=UnitPlugIn, provider=self, validate=validate,
            validation_kwargs=validation_kwargs, check=check, context=context)

    def _setup_translations(self):
        if self._gettext_domain and self._locale_dir:
            gettext.bindtextdomain(self._gettext_domain, self._locale_dir)

    @classmethod
    def from_definition(cls, definition, secure, *,
                        validate=True, validation_kwargs=None, check=False,
                        context=None):
        """
        Initialize a provider from Provider1Definition object

        :param definition:
            A Provider1Definition object to use as reference
        :param secure:
            Value of the secure flag. This cannot be expressed by a definition
            object.
        :param validate:
            Enable job validation. Incorrect job definitions will not be loaded
            and will abort the process of loading of the remainder of the jobs.
            This is ON by default to prevent broken job definitions from being
            used. This is a keyword-only argument.
        :param validation_kwargs:
            Keyword arguments to pass to the JobDefinition.validate().  Note,
            this is a single argument. This is a keyword-only argument.

        This method simplifies initialization of a Provider1 object where the
        caller already has a Provider1Definition object. Depending on the value
        of ``definition.location`` all of the directories are either None or
        initialized to a *good* (typical) value relative to *location*

        The only value that you may want to adjust, for working with source
        providers, is *locale_dir*, by default it would be ``location/locale``
        but ``manage.py i18n`` creates ``location/build/mo``
        """
        logger.debug("Loading provider from definition %r", definition)
        # Initialize the provider object
        return cls(
            definition.name, definition.version, definition.description,
            secure, definition.effective_gettext_domain,
            definition.effective_units_dir, definition.effective_jobs_dir,
            definition.effective_whitelists_dir, definition.effective_data_dir,
            definition.effective_bin_dir, definition.effective_locale_dir,
            definition.location or None, validate=validate,
            validation_kwargs=validation_kwargs, check=check, context=context)

    def __repr__(self):
        return "<{} name:{!r}>".format(self.__class__.__name__, self.name)

    @property
    def name(self):
        """
        name of this provider
        """
        return self._name

    @property
    def namespace(self):
        """
        namespace component of the provider name

        This property defines the namespace in which all provider jobs are
        defined in. Jobs within one namespace do not need to be fully qualified
        by prefixing their partial identifier with provider namespace (so all
        stays 'as-is'). Jobs that need to interact with other provider
        namespaces need to use the fully qualified job identifier instead.

        The identifier is defined as the part of the provider name, up to the
        colon. This effectively gives organizations flat namespace within one
        year-domain pair and allows to create private namespaces by using
        sub-domains.
        """
        return self._name.split(':', 1)[0]

    @property
    def version(self):
        """
        version of this provider
        """
        return self._version

    @property
    def description(self):
        """
        description of this provider
        """
        return self._description

    def tr_description(self):
        """
        Get the translated version of :meth:`description`
        """
        return self.get_translated_data(self.description)

    @property
    def units_dir(self):
        """
        absolute path of the units directory
        """
        return self._units_dir

    @property
    def jobs_dir(self):
        """
        absolute path of the jobs directory
        """
        return self._jobs_dir

    @property
    def whitelists_dir(self):
        """
        absolute path of the whitelist directory
        """
        return self._whitelists_dir

    @property
    def data_dir(self):
        """
        absolute path of the data directory
        """
        return self._data_dir

    @property
    def bin_dir(self):
        """
        absolute path of the bin directory

        .. note::
            The programs in that directory may not work without setting
            PYTHONPATH and CHECKBOX_SHARE.
        """
        return self._bin_dir

    @property
    def locale_dir(self):
        """
        absolute path of the directory with locale data

        The value is applicable as argument bindtextdomain()
        """
        return self._locale_dir

    @property
    def base_dir(self):
        """
        path of the directory with (perhaps) all of jobs_dir, whitelist_dir,
        data_dir, bin_dir, locale_dir. This may be None
        """
        return self._base_dir

    @property
    def build_bin_dir(self):
        """
        absolute path of the build/bin directory

        This value may be None. It depends on location/base_dir being set.
        """
        if self.base_dir is not None:
            return os.path.join(self.base_dir, 'build', 'bin')

    @property
    def src_dir(self):
        """
        absolute path of the src/ directory

        This value may be None. It depends on location/base_dir set.
        """
        if self.base_dir is not None:
            return os.path.join(self.base_dir, 'src')

    @property
    def CHECKBOX_SHARE(self):
        """
        required value of CHECKBOX_SHARE environment variable.

        .. note::
            This variable is only required by one script.
            It would be nice to remove this later on.
        """
        return self.base_dir

    @property
    def extra_PYTHONPATH(self):
        """
        additional entry for PYTHONPATH, if needed.

        This entry is required for CheckBox scripts to import the correct
        CheckBox python libraries.

        .. note::
            The result may be None
        """
        return None

    @property
    def secure(self):
        """
        flag indicating that this provider was loaded from the secure portion
        of PROVIDERPATH and thus can be used with the
        plainbox-trusted-launcher-1.
        """
        return self._secure

    @property
    def gettext_domain(self):
        """
        the name of the gettext domain associated with this provider

        This value may be empty, in such case provider data cannot be localized
        for the user environment.
        """
        return self._gettext_domain

    def get_builtin_whitelists(self):
        """
        Load all the whitelists from :attr:`whitelists_dir` and return them

        This method looks at the whitelist directory and loads all files ending
        with .whitelist as a WhiteList object.

        :returns:
            A list of :class:`~plainbox.impl.secure.qualifiers.WhiteList`
            objects sorted by
            :attr:`plainbox.impl.secure.qualifiers.WhiteList.name`.
        :raises IOError, OSError:
            if there were any problems accessing files or directories.  Note
            that OSError is silently ignored when the `whitelists_dir`
            directory is missing.
        """
        self._whitelist_collection.load()
        if self._whitelist_collection.problem_list:
            raise self._whitelist_collection.problem_list[0]
        else:
            return sorted(self._whitelist_collection.get_all_plugin_objects(),
                          key=lambda whitelist: whitelist.name)

    def get_builtin_jobs(self):
        """
        Load and parse all of the job definitions of this provider.

        :returns:
            A sorted list of JobDefinition objects
        :raises RFC822SyntaxError:
            if any of the loaded files was not valid RFC822
        :raises IOError, OSError:
            if there were any problems accessing files or directories.
            Note that OSError is silently ignored when the `jobs_dir`
            directory is missing.

        ..note::
            This method should not be used anymore. Consider transitioning your
            code to :meth:`load_all_jobs()` which is more reliable.
        """
        job_list, problem_list = self.load_all_jobs()
        if problem_list:
            raise problem_list[0]
        else:
            return job_list

    def load_all_jobs(self):
        """
        Load and parse all of the job definitions of this provider.

        Unlike :meth:`get_builtin_jobs()` this method does not stop after the
        first problem encountered and instead collects all of the problems into
        a list which is returned alongside the job list.

        :returns:
            Pair (job_list, problem_list) where each job_list is a sorted list
            of JobDefinition objects and each item from problem_list is an
            exception.
        """
        unit_list, problem_list = self.get_units()
        unit_list = [unit for unit in unit_list
                     if unit.Meta.name == 'job']
        unit_list.sort(key=lambda unit: unit.id)
        return unit_list, problem_list

    def get_units(self):
        """
        Get all units.

        :returns:
            Pair (unit_list, problem_list) where unit_list is a unsorted list
            of units, as they showed up in subsequent unit definition files and
            each item from problem_list is an exception.
        """
        self._unit_collection.load()
        self._whitelist_collection.load()
        unit_list = []
        for sublist in self._unit_collection.get_all_plugin_objects():
            unit_list.extend(sublist)
        for plugin in self._whitelist_collection.get_all_plugins():
            unit_list.extend(plugin.unit_list)
        problem_list = (self._unit_collection.problem_list
                        + self._whitelist_collection.problem_list)
        return unit_list, problem_list

    def get_all_executables(self):
        """
        Discover and return all executables offered by this provider

        :returns:
            list of executable names (without the full path)
        :raises IOError, OSError:
            if there were any problems accessing files or directories. Note
            that OSError is silently ignored when the `bin_dir` directory is
            missing.
        """
        return sorted(
            self._get_executables(self.bin_dir) +
            self._get_build_bin_executable_list())

    def _get_build_bin_executable_list(self):
        """
        Discover executables that are a part of the build/bin directory.

        The build/bin directory may contain nothing, standalone executables or
        a whole mess of build artifacts, only some of which are relevant. This
        method implements the following algorithm:

        * If the src/EXECUTABLES file exists then it must contain the name
          of each executable relative to the build/bin directory (typically
          just the name)
        * Otherwise all executable files from the build/bin directory are
          returned
        """
        if self.src_dir is not None:
            hint_file = os.path.join(self.src_dir, 'EXECUTABLES')
            if os.path.isfile(hint_file):
                with open(hint_file, "rt", encoding='UTF-8') as stream:
                    return [os.path.join(self.build_bin_dir, line.strip())
                            for line in stream if line.strip()]
        return self._get_executables(self.build_bin_dir)

    def _get_executables(self, dirname):
        executable_list = []
        if dirname is None:
            return executable_list
        try:
            items = os.listdir(dirname)
        except OSError as exc:
            if exc.errno == errno.ENOENT:
                items = []
            else:
                raise
        for name in items:
            filename = os.path.join(dirname, name)
            if os.access(filename, os.F_OK | os.X_OK):
                executable_list.append(filename)
        return executable_list

    def get_translated_data(self, msgid):
        """
        Get a localized piece of data

        :param msgid:
            data to translate
        :returns:
            translated data obtained from the provider if msgid is not False
            (empty string and None both are) and this provider has a
            gettext_domain defined for it, msgid itself otherwise.
        """
        if msgid and self._gettext_domain:
            return gettext.dgettext(self._gettext_domain, msgid)
        else:
            return msgid


class IQNValidator(PatternValidator):
    """
    A validator for provider name.

    Provider names use a RFC3720 IQN-like identifiers composed of the follwing
    parts:

    * year
    * (dot separating the next section)
    * domain name
    * (colon separating the next section)
    * identifier

    Each of the fields has an informal definition below:

        year:
            four digit number
        domain name:
            identifiers separated by dots, at least one dot has to be present
        identifier:
            `[a-z][a-z0-9-]*`
    """

    def __init__(self):
        super(IQNValidator, self).__init__(
            "^[0-9]{4}\.[a-z][a-z0-9-]*(\.[a-z][a-z0-9-]*)+:[a-z][a-z0-9-]*$")

    def __call__(self, variable, new_value):
        if super(IQNValidator, self).__call__(variable, new_value):
            return _("must look like RFC3720 IQN")


class VersionValidator(PatternValidator):
    """
    A validator for provider provider version.

    Provider version must be a sequence of non-negative numbers separated by
    dots. At most one version number must be present, which may be followed by
    any sub-versions.
    """

    def __init__(self):
        super().__init__("^[0-9]+(\.[0-9]+)*$")

    def __call__(self, variable, new_value):
        if super().__call__(variable, new_value):
            return _("must be a sequence of digits separated by dots")


class ExistingDirectoryValidator(IValidator):
    """
    A validator that checks that the value points to an existing directory
    """

    def __call__(self, variable, new_value):
        if not os.path.isdir(new_value):
            return _("no such directory")


class AbsolutePathValidator(IValidator):
    """
    A validator that checks that the value is an absolute path
    """

    def __call__(self, variable, new_value):
        if not os.path.isabs(new_value):
            return _("cannot be relative")


class Provider1Definition(Config):
    """
    A Config-like class for parsing plainbox provider definition files

    .. note::

        The location attribute is special, if set, it defines the base
        directory of *all* the other directory attributes. If location is
        unset, then all the directory attributes default to None (that is,
        there is no directory of that type). This is actually a convention that
        is implemented in :class:`Provider1PlugIn`. Here, all the attributes
        can be Unset and their validators only check values other than Unset.
    """

    location = Variable(
        section='PlainBox Provider',
        help_text=_("Base directory with provider data"),
        validator_list=[
            # NOTE: it *can* be unset!
            NotEmptyValidator(),
            AbsolutePathValidator(),
            ExistingDirectoryValidator(),
        ])

    name = Variable(
        section='PlainBox Provider',
        help_text=_("Name of the provider"),
        validator_list=[
            NotUnsetValidator(),
            NotEmptyValidator(),
            IQNValidator(),
        ])

    @property
    def name_without_colon(self):
        return self.name.replace(':', '.')

    version = Variable(
        section='PlainBox Provider',
        help_text=_("Version of the provider"),
        validator_list=[
            NotUnsetValidator(),
            NotEmptyValidator(),
            VersionValidator(),
        ])

    description = Variable(
        section='PlainBox Provider',
        help_text=_("Description of the provider"))

    gettext_domain = Variable(
        section='PlainBox Provider',
        help_text=_("Name of the gettext domain for translations"),
        validator_list=[
            # NOTE: it *can* be unset!
            PatternValidator("[a-z0-9_-]+"),
        ])

    @property
    def effective_gettext_domain(self):
        """
        effective value of gettext_domian

        The effective value is :meth:`gettex_domain` itself, unless it is
        Unset. If it is Unset the effective value None.
        """
        if self.gettext_domain is not Unset:
            return self.gettext_domain

    units_dir = Variable(
        section='PlainBox Provider',
        help_text=_("Pathname of the directory with unit definitions"),
        validator_list=[
            # NOTE: it *can* be unset
            NotEmptyValidator(),
            AbsolutePathValidator(),
            ExistingDirectoryValidator(),
        ])

    @property
    def implicit_units_dir(self):
        """
        implicit value of units_dir (if Unset)

        The implicit value is only defined if location is not Unset. It is the
        'units' subdirectory of the directory that location points to.
        """
        if self.location is not Unset:
            return os.path.join(self.location, "units")

    @property
    def effective_units_dir(self):
        """
        effective value of units_dir

        The effective value is :meth:`units_dir` itself, unless it is Unset. If
        it is Unset the effective value is the :meth:`implicit_units_dir`, if
        that value would be valid. The effective value may be None.
        """
        if self.units_dir is not Unset:
            return self.units_dir
        implicit = self.implicit_units_dir
        if implicit is not None and os.path.isdir(implicit):
            return implicit

    jobs_dir = Variable(
        section='PlainBox Provider',
        help_text=_("Pathname of the directory with job definitions"),
        validator_list=[
            # NOTE: it *can* be unset
            NotEmptyValidator(),
            AbsolutePathValidator(),
            ExistingDirectoryValidator(),
        ])

    @property
    def implicit_jobs_dir(self):
        """
        implicit value of jobs_dir (if Unset)

        The implicit value is only defined if location is not Unset. It is the
        'jobs' subdirectory of the directory that location points to.
        """
        if self.location is not Unset:
            return os.path.join(self.location, "jobs")

    @property
    def effective_jobs_dir(self):
        """
        effective value of jobs_dir

        The effective value is :meth:`jobs_dir` itself, unless it is Unset. If
        it is Unset the effective value is the :meth:`implicit_jobs_dir`, if
        that value would be valid. The effective value may be None.
        """
        if self.jobs_dir is not Unset:
            return self.jobs_dir
        implicit = self.implicit_jobs_dir
        if implicit is not None and os.path.isdir(implicit):
            return implicit

    whitelists_dir = Variable(
        section='PlainBox Provider',
        help_text=_("Pathname of the directory with whitelists definitions"),
        validator_list=[
            # NOTE: it *can* be unset
            NotEmptyValidator(),
            AbsolutePathValidator(),
            ExistingDirectoryValidator(),
        ])

    @property
    def implicit_whitelists_dir(self):
        """
        implicit value of whitelists_dir (if Unset)

        The implicit value is only defined if location is not Unset. It is the
        'whitelists' subdirectory of the directory that location points to.
        """
        if self.location is not Unset:
            return os.path.join(self.location, "whitelists")

    @property
    def effective_whitelists_dir(self):
        """
        effective value of whitelists_dir

        The effective value is :meth:`whitelists_dir` itself, unless it is
        Unset. If it is Unset the effective value is the
        :meth:`implicit_whitelists_dir`, if that value would be valid. The
        effective value may be None.
        """
        if self.whitelists_dir is not Unset:
            return self.whitelists_dir
        implicit = self.implicit_whitelists_dir
        if implicit is not None and os.path.isdir(implicit):
            return implicit

    data_dir = Variable(
        section='PlainBox Provider',
        help_text=_("Pathname of the directory with provider data"),
        validator_list=[
            # NOTE: it *can* be unset
            NotEmptyValidator(),
            AbsolutePathValidator(),
            ExistingDirectoryValidator(),
        ])

    @property
    def implicit_data_dir(self):
        """
        implicit value of data_dir (if Unset)

        The implicit value is only defined if location is not Unset. It is the
        'data' subdirectory of the directory that location points to.
        """
        if self.location is not Unset:
            return os.path.join(self.location, "data")

    @property
    def effective_data_dir(self):
        """
        effective value of data_dir

        The effective value is :meth:`data_dir` itself, unless it is Unset. If
        it is Unset the effective value is the :meth:`implicit_data_dir`, if
        that value would be valid. The effective value may be None.
        """
        if self.data_dir is not Unset:
            return self.data_dir
        implicit = self.implicit_data_dir
        if implicit is not None and os.path.isdir(implicit):
            return implicit

    bin_dir = Variable(
        section='PlainBox Provider',
        help_text=_("Pathname of the directory with provider executables"),
        validator_list=[
            # NOTE: it *can* be unset
            NotEmptyValidator(),
            AbsolutePathValidator(),
            ExistingDirectoryValidator(),
        ])

    @property
    def implicit_bin_dir(self):
        """
        implicit value of bin_dir (if Unset)

        The implicit value is only defined if location is not Unset. It is the
        'bin' subdirectory of the directory that location points to.
        """
        if self.location is not Unset:
            return os.path.join(self.location, "bin")

    @property
    def effective_bin_dir(self):
        """
        effective value of bin_dir

        The effective value is :meth:`bin_dir` itself, unless it is Unset. If
        it is Unset the effective value is the :meth:`implicit_bin_dir`, if
        that value would be valid. The effective value may be None.
        """
        if self.bin_dir is not Unset:
            return self.bin_dir
        implicit = self.implicit_bin_dir
        if implicit is not None and os.path.isdir(implicit):
            return implicit

    locale_dir = Variable(
        section='PlainBox Provider',
        help_text=_("Pathname of the directory with locale data"),
        validator_list=[
            # NOTE: it *can* be unset
            NotEmptyValidator(),
            AbsolutePathValidator(),
            ExistingDirectoryValidator(),
        ])

    @property
    def implicit_locale_dir(self):
        """
        implicit value of locale_dir (if Unset)

        The implicit value is only defined if location is not Unset. It is the
        'locale' subdirectory of the directory that location points to.
        """
        if self.location is not Unset:
            return os.path.join(self.location, "locale")

    @property
    def implicit_build_locale_dir(self):
        """
        implicit value of locale_dir (if Unset) as laid out in the source tree

        This value is only applicable to source layouts, where the built
        translation catalogs are in the build/mo directory.
        """
        if self.location is not Unset:
            return os.path.join(self.location, "build", "mo")

    @property
    def effective_locale_dir(self):
        """
        effective value of locale_dir

        The effective value is :meth:`locale_dir` itself, unless it is Unset.
        If it is Unset the effective value is the :meth:`implicit_locale_dir`,
        if that value would be valid. The effective value may be None.
        """
        if self.locale_dir is not Unset:
            return self.locale_dir
        implicit1 = self.implicit_locale_dir
        if implicit1 is not None and os.path.isdir(implicit1):
            return implicit1
        implicit2 = self.implicit_build_locale_dir
        if implicit2 is not None and os.path.isdir(implicit2):
            return implicit2


class Provider1PlugIn(IPlugIn):
    """
    A specialized IPlugIn that loads Provider1 instances from their definition
    files
    """

    def __init__(self, filename, definition_text, load_time, *, validate=None,
                 validation_kwargs=None, check=None, context=None):
        """
        Initialize the plug-in with the specified name and external object
        """
        start = now()
        self._load_time = load_time
        definition = Provider1Definition()
        # Load the provider definition
        definition.read_string(definition_text)
        # any validation issues prevent plugin from being used
        if definition.problem_list:
            # take the earliest problem and report it
            exc = definition.problem_list[0]
            raise PlugInError(
                _("Problem in provider definition, field {!a}: {}").format(
                    exc.variable.name, exc.message))
        # Get the secure flag
        secure = os.path.dirname(filename) in get_secure_PROVIDERPATH_list()
        # Initialize the provider object
        self._provider = Provider1.from_definition(
            definition, secure, validate=validate,
            validation_kwargs=validation_kwargs, check=check, context=context)
        self._wrap_time = now() - start

    def __repr__(self):
        return "<{!s} plugin_name:{!r}>".format(
            type(self).__name__, self.plugin_name)

    @property
    def plugin_name(self):
        """
        plugin name, the namespace of the provider
        """
        return self._provider.name

    @property
    def plugin_object(self):
        """
        plugin object, the actual Provider1 instance
        """
        return self._provider

    @property
    def plugin_load_time(self) -> float:
        """
        time, in fractional seconds, that was needed to load the provider
        definition file from the file system
        """
        return self._load_time

    @property
    def plugin_wrap_time(self) -> float:
        """
        time, in fractional seconds, that was needed to load the provider from
        the definition text
        """
        return self._wrap_time


def get_secure_PROVIDERPATH_list():
    """
    Computes the secure value of PROVIDERPATH

    This value is used by `plainbox-trusted-launcher-1` executable to discover
    all secure providers.

    :returns:
        A list of two strings:
        * `/usr/local/share/plainbox-providers-1`
        * `/usr/share/plainbox-providers-1`
    """
    return ["/usr/local/share/plainbox-providers-1",
            "/usr/share/plainbox-providers-1"]


class SecureProvider1PlugInCollection(FsPlugInCollection):
    """
    A collection of v1 provider plugins.

    This FsPlugInCollection subclass carries proper, built-in defaults, that
    make loading providers easier.

    This particular class loads providers from the system-wide managed
    locations. This defines the security boundary, as if someone can compromise
    those locations then they already own the corresponding system. In
    consequence this plug in collection does not respect ``PROVIDERPATH``, it
    cannot be customized to load provider definitions from any other location.
    This feature is supported by the
    :class:`plainbox.impl.providers.v1.InsecureProvider1PlugInCollection`
    """

    def __init__(self, **kwargs):
        dir_list = get_secure_PROVIDERPATH_list()
        super().__init__(dir_list, '.provider', wrapper=Provider1PlugIn,
                         **kwargs)


# Collection of all providers
all_providers = SecureProvider1PlugInCollection()
