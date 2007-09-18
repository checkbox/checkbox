import warnings
warnings.filterwarnings(action='ignore', category=FutureWarning)

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
