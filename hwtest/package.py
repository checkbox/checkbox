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
        self._packages = []

    def get_packages(self):
        if not self._packages:
            # The apt API not stable yet, so this filters warnings
            import warnings
            warnings.filterwarnings(action='ignore', category=FutureWarning)

            # Importing from the cache module is expensive, so this
            # delays the call until absolutely necessary
            from apt.cache import Cache

            for apt_package in Cache():
                if apt_package.isInstalled:
                    package = Package(apt_package)
                    self._packages.append(package)

        return self._packages
