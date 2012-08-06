#!/usr/bin/env python3

import os
import sys
import tempfile
import random
import string

from datetime import datetime, timedelta

TIMEOUT = timedelta(seconds=3)
BLOCKSIZE = 1024


def main():
    """
    Write/Read to/from temporary file to check HDD LED is working properly
    """
    starttime = datetime.now()

    print("Writing...")
    with tempfile.NamedTemporaryFile('wb', delete=False) as write_fh:
        # Create temporary file with random contents
        while (datetime.now() - starttime) < TIMEOUT:
            data = random.choice(string.printable) * BLOCKSIZE
            write_fh.write(data.encode('UTF-8'))

    print("Reading...")
    with open(write_fh.name, 'rb') as read_fh:
        # Read temporary file previously created
        while (datetime.now() - starttime) < 2 * TIMEOUT:
            data = read_fh.read(BLOCKSIZE)
            if not data:
                # Read file again from the beggining
                # until timeout has expired
                read_fh.seek(0)

    # Remove temporary file
    os.remove(write_fh.name)

    print("Success")
    return 0


if __name__ == "__main__":
    sys.exit(main())
