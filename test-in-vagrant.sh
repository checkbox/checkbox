#!/bin/sh
# Run all tests in various versions of Ubuntu via vagrant

mkdir -p vagrant-logs

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

outcome=0
# XXX: this list needs to be in sync with Vagrantfile
target_list="precise quantal"
for target in $target_list; do
    # Bring up target if needed
    if ! vagrant status $target | grep -q running; then
        echo "[$target] Bringing VM 'up'"
        if ! vagrant up $target >vagrant-logs/$target.startup.log 2>vagrant-logs/$target.startup.err; then
            outcome=1
            echo "[$target] Unable to 'up' VM!"
            echo "[$target] stdout: $(pastebinit vagrant-logs/$target.startup.log)"
            echo "[$target] stderr: $(pastebinit vagrant-logs/$target.startup.err)"
            echo "[$target] NOTE: unable to execute tests, marked as failed"
            continue
        fi
    fi
    # Display something before the first test output
    echo "[$target] Starting tests..."
    # Run checkbox unit tests
    if vagrant ssh $target -c 'cd checkbox && ./test' >vagrant-logs/$target.checkbox.log 2>vagrant-logs/$target.checkbox.err; then
        echo "[$target] CheckBox test suite: pass"
    else
        outcome=1
        echo "[$target] CheckBox test suite: fail"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.checkbox.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.checkbox.err)"
    fi
    # Run plainbox unit tests
    # TODO: It would be nice to support fast failing here
    if vagrant ssh $target -c 'cd checkbox/plainbox && python3 setup.py test' >vagrant-logs/$target.plainbox.log 2>vagrant-logs/$target.plainbox.err; then
        echo "[$target] PlainBox test suite: pass"
    else
        outcome=1
        echo "[$target] PlainBox test suite: fail"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.plainbox.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.plainbox.err)"
    fi
    # Run plainbox integration test suite (that tests checkbox scripts)
    if vagrant ssh $target -c 'sudo plainbox self-test --verbose --fail-fast --integration-tests' >vagrant-logs/$target.self-test.log 2>vagrant-logs/$target.self-test.err; then
        echo "[$target] Integration tests: pass"
    else
        outcome=1
        echo "[$target] Integration tests: fail"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.self-test.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.self-test.err)"
    fi
    # Suspend the target to conserve resources
    echo "[$target] Suspending VM"
    if ! vagrant suspend $target >vagrant-logs/$target.suspend.log 2>vagrant-logs/$target.suspend.err; then
        echo "[$target] Unable to suspend VM!"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.suspend.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.suspend.err)"
        echo "[$target] You may need to manually 'vagrant destroy $target' to fix this"
    fi
done
# Propagate failure code outside
exit $outcome
