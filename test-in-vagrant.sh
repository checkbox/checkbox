#!/bin/sh
# Run all tests in various versions of Ubuntu via vagrant

mkdir -p vagrant-logs
TIMING=vagrant-logs/timing.dat

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
target_list="precise quantal raring"
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
            continue
        fi
        echo "Timing for $step"
        cat $TIMING
    fi
    # Display something before the first test output
    echo "[$target] Starting tests..."
    # Run checkbox unit tests
    if time -o $TIMING vagrant ssh $target -c 'cd checkbox && ./test' >vagrant-logs/$target.checkbox.log 2>vagrant-logs/$target.checkbox.err; then
        echo "[$target] CheckBox test suite: pass"
    else
        outcome=1
        echo "[$target] CheckBox test suite: fail"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.checkbox.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.checkbox.err)"
    fi
    echo "Timing for Checkbox test suite"
    cat $TIMING
    # Refresh plainbox installation. This is needed if .egg-info (which is
    # essential for 'develop' to work) was removed in the meantime, for
    # example, by tarmac.
    if ! time -o $TIMING vagrant ssh $target -c 'cd checkbox/plainbox && python3 setup.py egg_info' >vagrant-logs/$target.egginfo.log 2>vagrant-logs/$target.egginfo.err; then
        outcome=1
        echo "[$target] Running 'plainbox/setup.py egg_info' failed"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.egginfo.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.egginfo.err)"
        echo "[$target] NOTE: unable to execute tests, marked as failed"
    fi
    echo "Timing for refreshing plainbox installation"
    cat $TIMING
    # Run plainbox unit tests
    # TODO: It would be nice to support fast failing here
    if time -o $TIMING vagrant ssh $target -c 'cd checkbox/plainbox && python3 setup.py test' >vagrant-logs/$target.plainbox.log 2>vagrant-logs/$target.plainbox.err; then
        echo "[$target] PlainBox test suite: pass"
    else
        outcome=1
        echo "[$target] PlainBox test suite: fail"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.plainbox.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.plainbox.err)"
    fi
    echo "Timing for plainbox test suite"
    cat $TIMING
    # Build plainbox documentation
    if time -o $TIMING vagrant ssh $target -c 'cd checkbox/plainbox && python3 setup.py build_sphinx' >vagrant-logs/$target.sphinx.log 2>vagrant-logs/$target.sphinx.err; then
        echo "[$target] PlainBox documentation build: pass"
    else
        outcome=1
        echo "[$target] PlainBox documentation build: fail"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.sphinx.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.sphinx.err)"
    fi
    echo "Timing for plainbox documentation build"
    cat $TIMING
    # Run plainbox integration test suite (that tests checkbox scripts)
    if time -o $TIMING vagrant ssh $target -c 'sudo plainbox self-test --verbose --fail-fast --integration-tests' >vagrant-logs/$target.self-test.log 2>vagrant-logs/$target.self-test.err; then
        echo "[$target] Integration tests: pass"
    else
        outcome=1
        echo "[$target] Integration tests: fail"
        echo "[$target] stdout: $(pastebinit vagrant-logs/$target.self-test.log)"
        echo "[$target] stderr: $(pastebinit vagrant-logs/$target.self-test.err)"
    fi
    echo "Timing for integration tests"
    cat $TIMING
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
