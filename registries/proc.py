from directory import DirectoryRegistry


class ProcRegistry(DirectoryRegistry):

    default_directory = "/proc"


factory = ProcRegistry
