#!/bin/sh
# Run all tests in various versions of Ubuntu via vagrant

mkdir -p vagrant-logs
TIMING=vagrant-logs/timing.dat
VAGRANT_DONE_ACTION=${VAGRANT_DONE_ACTION:-destroy}


pastebinit() {
    /usr/bin/python /usr/bin/pastebinit "$@";
}

test -z $(which vagrant) && echo "You need to install vagrant first" && exit

# When running in tarmac, the state file .vagrant, will be removed when the
# tree is re-pristinized. To work around that, check for present
# VAGRANT_STATE_FILE (custom variable, not set by tarmac or respected by
# vagrant) and symlink the .vagrant state file from there.
if [ "x$VAGRANT_STATE_FILE" != "x" ]; then
    if [ ! -e "$VAGRANT_STATE_FILE" ]; then
        touch "$VAGRANT_STATE_FILE"
    fi
    ln -fs "$VAGRANT_STATE_FILE" .vagrant
fi

if [ "$1" = "" ]; then
    # Vagrantfile defines several ubuntu target releases, the ones
    # we actually want to test in should be included in target_list below.
    target_list="precise trusty"
else
    target_list="$1"
fi

PASS="$(printf "\33[32;1mPASS\33[39;0m")"
FAIL="$(printf "\33[31;1mFAIL\33[39;0m")"

outcome=0
for target in $target_list; do
    # Bring up target if needed
    if ! vagrant status $target | grep -q running; then
        step="[$target] Bringing VM 'up'"
        echo $step
        if ! time -o $TIMING vagrant up $target >vagrant-logs/$target.startup.log 2>vagrant-logs/$target.startup.err; then
            outcome=1
            echo "[$target] Unable to 'up' VM!"
            echo "[$target] stdout: $(pastebinit vagrant-logs/$target.startup.log)"
            echo "[$target] stderr: $(pastebinit vagrant-logs/$target.startup.err)"
            echo "[$target] NOTE: unable to execute tests, marked as failed"
            echo "[$target] Destroying failed VM to reclaim resources"
            vagrant destroy -f $target;
            continue
        fi
        cat $TIMING | sed -e "s/^/[$target] (timing) /"
    fi
    # Display something before the first test output
    echo "[$target] Starting tests..."
    # Run test suite commands here.
    # Tests are found in each component's requirements/ dir and are named *container-tests-*
    # Numbers can be used at the beginning to control running order within each component.
    # Tests scripts are expected to:
    # - Be run from the *component's* top-level directory. This is a convenience to avoid
    #   a boilerplate "cd .." on every test script. So for 'plainbox' we do the equivalent of
    #   $ cd $BLAH/plainbox
    #   $
    # - Exit 0 for success, other codes for failure
    # - Write logs/debugging data to stdout and stderr.
    for test_script in $(find ./ -path '*/requirements/*container-tests-*' | sort); do
        echo "Found a test script: $test_script"
        test_name=$(basename $test_script)
        # Two dirnames strips the requirements/ component
        component_dir=$(dirname $(dirname $test_script))
        # Inside the VM, tests are relative to $HOME/src.
        # Note that for vagrant, we want $HOME to expand *inside* the VM, so
        # that part of the command is in *single* quotes, otherwise we get the
        # $HOME from the host. However, $component_dir and $test_name should
        # come from the host, so we use double quotes.
        script_md5sum=$(echo $test_script | md5sum |cut -d " " -f 1)
        logfile=vagrant-logs/${target}.${test_name}.${script_md5sum}.log
        errfile=vagrant-logs/${target}.${test_name}.${script_md5sum}.err
        if /usr/bin/time -o $TIMING vagrant ssh $target -c 'cd $HOME/src/'"$component_dir && ./requirements/$test_name" >$logfile 2>$errfile
        then
            echo "[$target] ${test_name}: $PASS"
        else
            outcome=1
            echo "[$target] ${test_name}: $FAIL"
            echo "[$target] stdout: $(pastebinit $logfile)"
            echo "[$target] stderr: $(pastebinit $errfile)"
        fi
        cat $TIMING | sed -e "s/^/[$target] (timing) /"
    done

    # Decide what to do with the VM
    case $VAGRANT_DONE_ACTION in
        suspend)
            # Suspend the target to conserve resources
            echo "[$target] Suspending VM"
            if ! vagrant suspend $target >vagrant-logs/$target.suspend.log 2>vagrant-logs/$target.suspend.err; then
                echo "[$target] Unable to suspend VM!"
                echo "[$target] stdout: $(pastebinit vagrant-logs/$target.suspend.log)"
                echo "[$target] stderr: $(pastebinit vagrant-logs/$target.suspend.err)"
                echo "[$target] You may need to manually 'vagrant destroy $target' to fix this"
            fi
            ;;
        destroy)
            # Destroy the target to work around virtualbox hostsf bug
            echo "[$target] Destroying VM"
            if ! vagrant destroy --force $target >vagrant-logs/$target.destroy.log 2>vagrant-logs/$target.destroy.err; then
                echo "[$target] Unable to destroy VM!"
                echo "[$target] stdout: $(pastebinit vagrant-logs/$target.suspend.log)"
                echo "[$target] stderr: $(pastebinit vagrant-logs/$target.suspend.err)"
                echo "[$target] You may need to manually 'vagrant destroy $target' to fix this"
            fi
            ;;
    esac
done
# Propagate failure code outside
exit $outcome
