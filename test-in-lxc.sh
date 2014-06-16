#!/bin/bash
# Run all tests in various versions of Ubuntu via lxc.
# Use of a local apt-cacher-ng instance and setting MIRROR in /etc/default/lxc
# is strongly recommended, to speed up creation of pristine images:
# MIRROR="http://localhost:3142/archive.ubuntu.com/ubuntu"
# lxc commands depend heavily on sudo. Edit your sudo configuration and give
# the user that will run these tests the ability to run lxc commands without
# password. Something like this works:
# Cmnd_Alias LXC_COMMANDS = /usr/bin/lxc-create, /usr/bin/lxc-start, \
# /usr/bin/lxc-destroy, /usr/bin/lxc-attach, /usr/bin/lxc-start-ephemeral, \
# /usr/bin/lxc-stop, /usr/bin/lxc-ls, /usr/bin/lxc-info, /usr/bin/lxc-wait
# your-user ALL=NOPASSWD: LXC_COMMANDS

LOG_DIR=lxc-logs
mkdir -p $LOG_DIR
TIMING=$LOG_DIR/timing.dat

pastebinit() {
    /usr/bin/python /usr/bin/pastebinit "$@";
}

# User-tunable options.
# KEEP_DATA is actually a set of options to lxc-start-ephemeral, notably it
# can contain "--keep-data", in which case it will use a directory-backed
# overlayfs to create the ephemeral VM. Setting KEEP_DATA to an empty string
# will put the overlayfs in ramdisk (tmpfs), which is much faster but
# requires more RAM (don't run this on a system with less than 3GB total RAM),
# so the default is to --keep-data.
KEEP_DATA=${KEEP_DATA:-"--keep-data"}
# The name of the user we will create inside the container, we will also
# run commands inside the container as this user, using sudo.
CONTAINER_USER=ubuntu

# Location of LXC executables.
LXC_CREATE=`which lxc-create`
LXC_START=`which lxc-start`
LXC_STOP=`which lxc-stop`
LXC_DESTROY=`which lxc-destroy`
LXC_START_EPHEMERAL=`which lxc-start-ephemeral`
LXC_ATTACH=`which lxc-attach`
LXC_LS=`which lxc-ls`
LXC_WAIT=`which lxc-wait`
LXC_INFO=`which lxc-info`

test_lxc_can_run(){
    PROBLEM=0
    for tool in "$LXC_CREATE" "$LXC_START" "$LXC_STOP" "$LXC_DESTROY" \
                "$LXC_ATTACH" "$LXC_WAIT" "$LXC_INFO"; do
    if [ -z "$tool" ]; then
        echo "lxc commands not found, maybe you need to install lxc"
        PROBLEM=1
    else
        if ! sudo -n $tool --version >/dev/null 2>&1; then
        PROBLEM=1
        echo "I can't run $tool, maybe you need to give me sudo permissions"
        fi
    fi
    done
    return $PROBLEM
}


start_lxc_for(){
    target=$1
    pristine_container=${1}-pristine
    target_container=${1}-testing
    [ "$target" != "" ] || return 1

    # Ensure we have a pristine container, create it otherwise.
    if ! sudo $LXC_LS |grep -q $pristine_container; then
        step="[$target] creating pristine container"
        echo $step
        if ! /usr/bin/time -o $TIMING sudo $LXC_CREATE  -n $pristine_container -t ubuntu -- -r $target --user=$CONTAINER_USER --packages=python-software-properties,software-properties-common >$LOG_DIR/$target.pristine.log 2>$LOG_DIR/$target.pristine.err; then
            outcome=1
            echo "[$target] Unable to create pristine container!"
            echo "[$target] stdout: $(pastebinit $LOG_DIR/$target.pristine.log)"
            echo "[$target] NOTE: unable to execute tests, marked as failed"
            echo "[$target] Trying to destroy to reclaim possible resources"
            sudo $LXC_DESTROY -f -n $pristine_container
            return
        fi
        cat $TIMING | sed -e "s/^/[$target] (timing) /"
        # TODO: Add --provision-pristine to do exactly that, that way it will be faster
        # at the expense of not updating dependencies for every run. It'll be useful
        # for testing. It's a bit hard because we can't do the bind mount (-b), an alternative
        # is to use -s to mimic bindmount (problem: target dir not created by default
    fi
    step="[$target] starting container"
    echo $step
    if ! /usr/bin/time -o $TIMING sudo $LXC_START_EPHEMERAL $KEEP_DATA -d -o $pristine_container -n $target_container -b $PWD >$LOG_DIR/$target.startup.log 2>$LOG_DIR/$target.startup.err; then
        outcome=1
        echo "[$target] Unable to start ephemeral container!"
        echo "[$target] stdout: $(pastebinit $LOG_DIR/$target.startup.log)"
        echo "[$target] stderr: $(pastebinit $LOG_DIR/$target.startup.err)"
        echo "[$target] NOTE: unable to execute tests, marked as failed"
        echo "[$target] Destroying failed container to reclaim resources"
        sudo $LXC_DESTROY -f -n $target_container
        return 1
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"

    # Before provisioning, try to detect and configure apt-cacher-ng
    if [ -n "$VAGRANT_APT_CACHE" ]; then
        # Explicitly set
        sudo $LXC_ATTACH --keep-env -n $target_container -- bash -c "echo 'Acquire::http { Proxy \"$VAGRANT_APT_CACHE\"; };' > /etc/apt/apt.conf"
    elif [ -e /etc/apt-cacher-ng ]; then
        # Autodetected local apt-cacher-ng, find out the host IP address to
        # pass into the container
        APT_CACHER_IP=$(ip route get 8.8.8.8 | awk 'NR==1 {print $NF}')
        [ -n "$APT_CACHER_IP" ] && sudo $LXC_ATTACH --keep-env -n $target_container -- bash -c "echo 'Acquire::http { Proxy \"http://$APT_CACHER_IP:3142\"; };' > /etc/apt/apt.conf"
    fi

    # Unlike with Vagrant, we have to provision the VM "manually" here.
    # However we can leverage the same script :D
    step="[$target] provisioning container"
    echo $step
    if ! /usr/bin/time -o $TIMING sudo $LXC_ATTACH --keep-env -n $target_container >$LOG_DIR/$target.provision.log 2>$LOG_DIR/$target.provision.err -- bash -c "support/provision-testing-environment $PWD"; then
        echo "[$target] Unable to provision requirements in container!"
        echo "[$target] stdout: $(pastebinit $LOG_DIR/$target.provision.log)"
        echo "[$target] stderr: $(pastebinit $LOG_DIR/$target.provision.err)"
        echo "[$target] NOTE: unable to execute tests, marked as failed"
        echo "[$target] Destroying failed container to reclaim resources"
        sudo $LXC_DESTROY -f -n $target_container
        return 1
    fi
    cat $TIMING | sed -e "s/^/[$target] (timing) /"
}


if [ "$1" = "" ]; then
    # Releases we actually want to test should be included in target_list below.
    target_list="precise trusty"
else
    target_list="$1"
fi

PASS="$(printf "\33[32;1mPASS\33[39;0m")"
FAIL="$(printf "\33[31;1mFAIL\33[39;0m")"

outcome=0

test_lxc_can_run || exit 1

for target_release in $target_list; do
    if ! start_lxc_for $target_release; then
        outcome=1
        continue
    fi
    # Our actual container has "-testing" appended.
    target=${target_release}-testing
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
        # Inside the LXC container, tests are relative to $HOME/src
        script_md5sum=$(echo $test_script | md5sum |cut -d " " -f 1)
        logfile=$LOG_DIR/${target}.${test_name}.${script_md5sum}.log
        errfile=$LOG_DIR/${target}.${test_name}.${script_md5sum}.err
        if /usr/bin/time -o $TIMING sudo $LXC_ATTACH --keep-env -n $target -- bash -c 'cd $HOME/src/'"$component_dir && ./requirements/$test_name" >$logfile 2>$errfile
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

    # Fix permissions.
    # provision-testing-environment runs as root and creates a series of
    # root-owned files in the branch directory. Later, tarmac will want
    # to delete these files, so after provisioning we change everything
    # under the branch directory to be owned by the unprivileged user,
    # so stuff can be deleted correctly later.
    if ! sudo $LXC_ATTACH --keep-env -n $target_container -- bash -c "chown -R --reference=test-in-lxc.sh $PWD" >$LOG_DIR/$target.fix-perms.log 2>$LOG_DIR/$target.fix-perms.err; then
        echo "[$target] Unable to fix permissions!"
        echo "[$target] stdout: $(pastebinit $LOG_DIR/$target.fix-perms.log)"
        echo "[$target] stderr: $(pastebinit $LOG_DIR/$target.fix-perms.err)"
        echo "[$target] Some files owned by root may have been left around, fix them manually with chown."
    fi

    echo "[$target] Destroying container"
    # Stop the container first
    if ! sudo $LXC_STOP -n $target >$LOG_DIR/$target.stop.log 2>$LOG_DIR/$target.stop.err; then
        echo "[$target] Unable to stop container!"
        echo "[$target] stdout: $(pastebinit $LOG_DIR/$target.stop.log)"
        echo "[$target] stderr: $(pastebinit $LOG_DIR/$target.stop.err)"
        echo "[$target] You may need to manually 'sudo lxc-stop -n $target' to fix this"
    fi
    # Wait for container to actually stop
    sudo $LXC_WAIT -n $target -s 'STOPPED'
    # If still present, then destroy it
    if sudo $LXC_INFO -n $target; then
        if ! sudo $LXC_DESTROY -n $target -f >$LOG_DIR/$target.destroy.log 2>$LOG_DIR/$target.destroy.err; then
            echo "[$target] Unable to destroy container!"
            echo "[$target] stdout: $(pastebinit $LOG_DIR/$target.destroy.log)"
            echo "[$target] stderr: $(pastebinit $LOG_DIR/$target.destroy.err)"
            echo "[$target] You may need to manually 'sudo lxc-destroy -f -n $target' to fix this"
        fi
    fi
done
# Propagate failure code outside
exit $outcome
