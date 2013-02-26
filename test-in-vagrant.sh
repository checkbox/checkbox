#!/bin/sh
# Run all tests in various versions of Ubuntu via vagrant

mkdir -p vagrant-logs

test -z $(which vagrant) && echo "You need to install vagrant first" && exit
# XXX: this list needs to be in sync with Vagrantfile
target_list="precise quantal"
for target in $target_list; do
    # Bring up target if needed
    if ! vagrant status $target | grep -q running; then
        vagrant up $target || ( echo "Unable to bring $target up [$?]" && continue )
    fi
    # Run checkbox unit tests
    if vagrant ssh $target -c 'cd checkbox && ./test' >vagrant-logs/$target.checkbox.log 2>vagrant-logs/$target.checkbox.err; then
        echo "CheckBox test suite [$target]: pass"
    else
        echo "CheckBox test suite [$target]: fail"
    fi
    # Run plainbox unit tests
    # TODO: It would be nice to support fast failing here
    if vagrant ssh $target -c 'cd checkbox/plainbox && python3 setup.py test' >vagrant-logs/$target.plainbox.log 2>vagrant-logs/$target.plainbox.err; then
        echo "PlainBox test suite [$target]: pass"
    else
        echo "PlainBox test suite [$target]: fail"
    fi
    # Run plainbox integration test suite (that tests checkbox scripts)
    if vagrant ssh $target -c 'sudo plainbox self-test --verbose --fail-fast --integration-tests' >vagrant-logs/$target.self-test.log 2>vagrant-logs/$target.self-test.err; then
        echo "Integration tests [$target]: pass"
    else
        echo "Integration tests [$target]: fail"
    fi
done
