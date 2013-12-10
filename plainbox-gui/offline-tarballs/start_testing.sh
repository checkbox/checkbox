#!/bin/bash

WANTED_PACKAGES="canonical-driver-test-suite"
START_TESTING_LOG=/tmp/start_testing.log
START_TESTING_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Use log to write stuff to the logfile, and optionally show it to
# the user if DEBUG is set.
function log(){
    echo "$@" >>$START_TESTING_LOG
    [ "$DEBUG" = "yes" ] && message "$@"
}

# Use message to inconditionally show stuff to the user.
function message(){
    echo $1
    if [ "$DEBUG" = "yes" ]; then
        echo "Press ENTER to proceed, or ctrl-c to exit"
        read
    fi
}

function pkexec_or_sudo(){
    which sudo >/dev/null && SUPER_COMMAND='sudo'
    which pkexec >/dev/null && SUPER_COMMAND='pkexec'
}

[ -f $START_TESTING_LOG ] && rm $START_TESTING_LOG

# Try to mock-install the package in question, apt-get results will tell me what
# to do next.
PACKAGES=$WANTED_PACKAGES
DRY_OUTPUT=$(apt-get install -y --force-yes --dry-run $PACKAGES 2>&1)
log "$DRY_OUTPUT"
ACTIONS=""
# If at least one package is unfindable, add the repos
if echo "$DRY_OUTPUT" | grep -q "Unable to locate"; then
    log "I need to add the repos and install $PACKAGES"
    message "This program needs to configure repositories and install packages."
    message "Your password will be requested for this action."
    ACTIONS="-u -i"
# If at least one package needs to be installed, then well, install.
elif echo "$DRY_OUTPUT" | grep -q "^Inst "; then
    log "I need to install $PACKAGES"
    message "This program needs to configure repositories and install packages."
    message "Your password will be requested for this action."
    ACTIONS=" -i"
    PACKAGES=$WANTED_PACKAGES
elif echo "$DRY_OUTPUT" | grep -q "already the newest version"; then
    log "I don't need to do anything"
else
    log "I don't know what happened :( Assuming I need to add repo and install"
    message "This program needs to configure repositories and install packages."
    message "Your password will be requested for this action."
    ACTIONS="-u -i"
    PACKAGES=$WANTED_PACKAGES
fi

if [ -n "$ACTIONS" ]; then
    pkexec_or_sudo
    $SUPER_COMMAND $START_TESTING_DIR/add_offline_repository $ACTIONS "$PACKAGES"
fi
cat <<EOF
To start canonical-driver-test-suite in graphical mode please open the dash and
search for 'canonical driver test suite'.

To start canonical-driver-test-suite in terminal mode, please press ctrl-alt-t
to open a terminal, then type 'canonical-driver-test-suite-cli' and press
ENTER.

Press ENTER to continue.
EOF

read confirmation
