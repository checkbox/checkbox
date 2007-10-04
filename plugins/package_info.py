import warnings
warnings.filterwarnings(action='ignore', category=FutureWarning)

from hwtest.plugin import Plugin
from hwtest.report_helpers import createElement, createTypedElement

from apt.cache import Cache


class Package(object):

    def __init__(self, apt_package):
        self._apt_package = apt_package

    @property
    def properties(self):
        package = self._apt_package
        return {
            "name": package.name,
            "priority": package.priority,
            "section": package.section,
            "source": package.sourcePackageName,
            "version": package.installedVersion,
            "installed_size": package.installedSize,
            "size": package.packageSize,
            "summary": package.summary}


class PackageManager(object):

    def __init__(self):
        self._cache = Cache()

    def get_packages(self):
        packages = []
        for apt_package in self._cache:
            if apt_package.isInstalled:
                package = Package(apt_package)
                packages.append(package)

        return packages


class PackageInfo(Plugin):

    def __init__(self, config, package_manager=None):
        super(PackageInfo, self).__init__(config)
        self._package_manager = package_manager or PackageManager()

    def gather(self):
        report = self._manager.report
        if not report.finalised:
            content = self.get_content()
            software = getattr(report, 'software', None)
            if software is None:
                software = createElement(report, 'software', report.root)
                report.software = software
            packages = createElement(report, 'packages', software)
            for package in content:
                name = package['name']
                del package['name']
                createTypedElement(report, 'package', packages, name, package,
                                   True)

    def get_content(self):
        content = []

        for package in self._package_manager.get_packages():
            properties = package.properties
            content.append(properties)

        return content


factory = PackageInfo
