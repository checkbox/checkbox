import os

# HTTP header to authenticate a machine.
MACHINE_ID_HEADER = "X-Machine-ID"

# HTTP header to define the API version.
MESSAGE_API_HEADER = "X-Message-API"

# Directory containing shared files.
HWTEST_DIR = os.environ.get("HWTEST_DIR") or '/usr/share/hwtest'
