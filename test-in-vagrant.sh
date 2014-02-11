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

    # Build checkbox-gui
    if time -o $TIMING vagrant ssh $target -c 'cd src/checkbox-gui; make distclean; qmake && make' >vagrant-logs/$target.checkbox-gui.log 2>vagrant-logs/$target.checkbox-gui.err; then
        echo "[$target] Checkbox GUI build: $PASS"
    else
        outcome=1
        echo "[$target] Checkbox GUI build: $FAIL"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.checkbox-gui.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.checkbox-gui.err)"
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"

    # Run checkbox unit tests
    if time -o $TIMING vagrant ssh $target -c 'cd src/checkbox-old && python3 setup.py test' >vagrant-logs/$target.checkbox.log 2>vagrant-logs/$target.checkbox.err; then
        echo "[$target] CheckBox test suite: $PASS"
    else
        outcome=1
        echo "[$target] CheckBox test suite: $FAIL"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.checkbox.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.checkbox.err)"
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"

    # Refresh plainbox installation. This is needed if .egg-info (which is
    # essential for 'develop' to work) was removed in the meantime, for
    # example, by tarmac.
    if ! time -o $TIMING vagrant ssh $target -c 'cd src/plainbox && python3 setup.py egg_info' >vagrant-logs/$target.egginfo.log 2>vagrant-logs/$target.egginfo.err; then
        outcome=1
        echo "[$target] Running 'plainbox/setup.py egg_info' failed"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.egginfo.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.egginfo.err)"
        echo "[$target] NOTE: unable to execute tests, marked as failed"
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"

    # Run plainbox unit tests
    # TODO: It would be nice to support fast failing here
    if time -o $TIMING vagrant ssh $target -c 'cd src/plainbox && python3 setup.py test' >vagrant-logs/$target.plainbox.log 2>vagrant-logs/$target.plainbox.err; then
        echo "[$target] PlainBox test suite: $PASS"
    else
        outcome=1
        echo "[$target] PlainBox test suite: $FAIL"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.plainbox.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.plainbox.err)"
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"

    # Build plainbox documentation
    if time -o $TIMING vagrant ssh $target -c 'cd src/plainbox && python3 setup.py build_sphinx' >vagrant-logs/$target.sphinx.log 2>vagrant-logs/$target.sphinx.err; then
        echo "[$target] PlainBox documentation build: $PASS"
    else
        outcome=1
        echo "[$target] PlainBox documentation build: $FAIL"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.sphinx.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.sphinx.err)"
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"

    # Run checkbox-ng unit tests
    if time -o $TIMING vagrant ssh $target -c 'cd src/checkbox-ng && python3 setup.py test' >vagrant-logs/$target.checkbox-ng.log 2>vagrant-logs/$target.checkbox-ng.err; then
        echo "[$target] CheckBoxNG test suite: $PASS"
    else
        outcome=1
        echo "[$target] CheckBoxNG test suite: $FAIL"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.checkbox-ng.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.checkbox-ng.err)"
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"

    # Run plainbox integration test suite (that tests checkbox scripts)
    if time -o $TIMING vagrant ssh $target -c 'sudo plainbox self-test --verbose --fail-fast --integration-tests' >vagrant-logs/$target.self-test.log 2>vagrant-logs/$target.self-test.err; then
        echo "[$target] Integration tests: $PASS"
    else
        outcome=1
        echo "[$target] Integration tests: $FAIL"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.self-test.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.self-test.err)"
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"

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
