#!/bin/sh
# Create a virtualenv in /ramdisk
#
# This is how Zygmunt Krynicki works, feel free to use or adjust to your needs

VENV_PATH=${1:-/ramdisk/venv}

if [ ! -d $(dirname $VENV_PATH) ]; then
    echo "This script requires $(dirname $VENV_PATH) directory to exist"
    exit 1
fi

if [ ! -d $VENV_PATH ]; then
    virtualenv -p python3 $VENV_PATH
    . $VENV_PATH/bin/activate
    easy_install -U distribute
    easy_install -U coverage
    python3 setup.py develop
fi

echo "To activate your virtualenv run"
echo " $ . $VENV_PATH/bin/activate"
