import os
import sys
import ConfigParser

from debconf import Debconf, DebconfCommunicator, DebconfError, MEDIUM


class Install(object):

    separator = "/"
    config_base = "/etc/hwtest.d/%(name)s.conf"
    example_base = "/usr/share/doc/%(name)s/examples/%(name)s.conf"

    def __init__(self, name, config_path=None, example_path=None, variables=[]):
        self.name = name
        self._variables = variables
        self._config_path = config_path or self.config_base % {"name": name}
        self._example_path = example_path or self.example_base % {"name": name}

        self._config = ConfigParser.ConfigParser()
        if os.environ.get("DEBIAN_HAS_FRONTEND"):
            if os.environ.get("DEBCONF_REDIR"):
                write = os.fdopen(3, "w")
            else:
                write = sys.stdout
            self._debconf = Debconf(write=write)
        else:
            self._debconf = DebconfCommunicator(self.name)

    def set_example(self, path):
        self._example_path = path

    def set_config(self, path):
        self._config_path = path

    def set_variables(self, variables):
        self._variables = variables

    def write(self, output):
        for path in [self._example_path, self._config_path]:
            if path and os.path.isfile(path):
                self._config.read(path)

        # Set configuration variables
        for variable in self._variables:
            section, name = variable.rsplit(self.separator, 1)
            value = self._debconf.get(variable)
            self._config.set(section, name, value)

        # Write config
        f = open(output, "w")
        self._config.write(f)
        f.close()

    def configure(self, priority=MEDIUM):
        path = self._config_path
        if path and os.path.isfile(path):
            self._config.read(path)

        # Set debconf variables
        for variable in self._variables:
            section, name = variable.rsplit(self.separator, 1)
            if self._config.has_option(section, name):
                self._debconf.set(variable, self._config.get(section, name))

        # Ask questions and set new values, if needed.
        step = 0
        while step < len(self._variables):
            if step < 0:
                raise Exception, "Stepped too far back."
            variable = self._variables[step]
            try:
                self._debconf.input(priority, variable)
            except DebconfError, e:
                if e.args[0] != 30:
                    raise
                # Question preivously answered and skipped.
                step += 1
            else:
                try:
                    self._debconf.go()
                except DebconfError, e:
                    if e.args[0] != 30:
                        raise
                    # User requested to go back.
                    step -= 1
                else:
                    step += 1
