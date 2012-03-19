#!/usr/bin/python

import dbus
import sys
import random
import os
import tempfile
import hashlib
import argparse
from shutil import copy2
import subprocess
import threading

class DiskTest():
    def __init__(self):
        self.process = None
        self.cmd = None
        self.timeout = 3
        self.returnCode = None
        self.rem_disks = {}     # mounted before the script running
        self.rem_disks_nm = {}  # not mounted before the script running

    ''' Class to contain various methods for testing USB disks '''
    def generate_test_data(self,size):
        '''Generate a random data file of a given size'''
        r = random
        min = 100
        max = 1000000
        self.tfile = tempfile.NamedTemporaryFile(delete=False)
        print "Creating Temp Data file"
        while os.path.getsize(self.tfile.name) < size:
            self.tfile.write(str(r.randint(min,max)))

        print "File name is :%s" % self.tfile.name
        print "File size is %s bytes" % os.path.getsize(self.tfile.name)

    def md5_hash_file(self,path):
        fh = open(path,'r')
        md5 = hashlib.md5()
        try:
            while True:
                data = fh.read(8192)
                if not data:
                    break
                md5.update(data)
        finally:
            fh.close()
        return md5.hexdigest()

    def copy_file(self,source,dest):
        try:
            copy2(source,dest)
        except IOError:
            print "ERROR: Unable to copy the file to %s" % dest
            return False
        else:
            return True

    def compare_hash(self,parent,child):
        if not parent == child:
            return False
        else:
            return True

    def clean_up(self,target):
        try:
            os.unlink(target)
        except:
            print "ERROR: Unable to remove tempfile %s" % target

    def get_disk_info(self, device):
        ''' Probes dbus to find any attached/mounted devices'''
        bus = dbus.SystemBus()
        ud_manager_obj = bus.get_object("org.freedesktop.UDisks", "/org/freedesktop/UDisks")
        ud_manager = dbus.Interface(ud_manager_obj, 'org.freedesktop.UDisks')
        self.rem_disks = {}
        self.rem_disks_nm = {}
        for dev in ud_manager.EnumerateDevices():
            device_obj = bus.get_object("org.freedesktop.UDisks", dev)
            device_props = dbus.Interface(device_obj, dbus.PROPERTIES_IFACE)
            if not device_props.Get('org.freedesktop.UDisks.Device',"DeviceIsDrive"):
                if device_props.Get('org.freedesktop.UDisks.Device', "DriveConnectionInterface") in device:
                    dev_file = str(device_props.Get('org.freedesktop.UDisks.Device',"DeviceFile"))

                    if len(device_props.Get('org.freedesktop.UDisks.Device',"DeviceMountPaths")) > 0:
                        devPath = str(device_props.Get('org.freedesktop.UDisks.Device',"DeviceMountPaths")[0])
                        self.rem_disks[dev_file] = devPath
                    else:
                        self.rem_disks_nm[dev_file] = None

    def mount(self):
        passed_mount = {}

        for k, _ in self.rem_disks_nm.items():
            t = tempfile.mkdtemp(dir='/tmp')
 
            r = False
            try:
                r = self.make_thread(self._mount(k, t))
            except:
                pass

            # remove those devices fail at mounting
            if r: 
                passed_mount[k] = t
                print "Now mounting %s on %s" % (k, t)
            else:
                print "Error: can't mount %s" % (k)
        
        if len(self.rem_disks_nm) == len(passed_mount):
            self.rem_disks_nm = passed_mount
            return 0
        else:
            c = len(self.rem_disks_nm) - len(passed_mount) 
            self.rem_disks_nm = passed_mount
            return c

    def _mount(self, dev_file, tmp_dir):
        cmd = ['/bin/mount', dev_file, tmp_dir]
        self.process = subprocess.Popen(cmd)
        self.process.communicate()

    def umount(self):
        errors = 0

        for d in self.rem_disks_nm:
            r = False
            try:
                r = self.make_thread(self._umount(d))
            except:
                errors += 1
                pass

            if r:
                print "Now umounting %s on %s" % (d, self.rem_disks_nm[d]) 
            else:
                print "Error: can't umount %s on %s" % (d, self.rem_disks_nm[d]) 

        return errors

    def _umount(self, dir):
        # '-l': lazy umount, dealing problem of unable to umount the device.
        cmd = ['/bin/umount', '-l', dir] 
        self.process = subprocess.Popen(cmd)
        self.process.communicate()

    def clean_tmp_dir(self):
        for d in self.rem_disks_nm:
            if not os.path.ismount(self.rem_disks_nm[d]):
                os.rmdir(self.rem_disks_nm[d])

    def make_thread(self, target):
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(self.timeout)

        if thread.is_alive():
            self.process.terminate()
            thread.join()

        r = getattr(self.process,'returncode', 1)

        if r == 0:
            return True
        else:
            return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('device',
                        choices=['usb','firewire','sdio', 'scsi'],
                        nargs = '+',
                        help="The type of removable media (usb, firewire, sdio) to test.")
    parser.add_argument('-l','--list',
                        action='store_true',
                        default=False,
                        help="List the removable devices and mounting status")
    parser.add_argument('-c','--count',
                        action='store',
                        default='1',
                        type=int,
                        help='The number of times to run the test')
    parser.add_argument('-s','--size',
                        action='store',
                        type=int,
                        default=1048576,
                        help="The size of the test data file to use in Bytes. Default is %(default)s")
    parser.add_argument('-n','--skip-not-mount',
                        action='store_true',
                        default=False,
                        help="skip the removable devices which haven't been mounted before the test.")

    args = parser.parse_args()

    test = DiskTest()
    test.get_disk_info(args.device)

    errors = 0

    if len(test.rem_disks) > 0 or len(test.rem_disks_nm) > 0: #If we do have removable drives attached and mounted
        if args.list:   #Simply output a list of drives detected
            print '-' * 20 
            print "removable devices currently mounted:"
            if len(test.rem_disks) > 0:
                for k,v in test.rem_disks.iteritems():
                    print "%s : %s" % (k, v)
            else:
                print "None"

            print "removable devices currently not mounted:"
            if len(test.rem_disks_nm) > 0:
                for k, _ in test.rem_disks_nm.iteritems():
                    print k
            else:
                print "None"
            
            print '-' * 20

            return 0

        else: #Create a file, copy to USB and compare hashes
            if args.skip_not_mount: 
                disks_all = test.rem_disks
            else:
                # mount those haven't be mounted yet.
                errors_mount = test.mount()

                if errors_mount > 0:
                    print "There're total %d device(s) failed at mounting." % errors_mount
                    errors += errors_mount

                disks_all = dict(test.rem_disks.items() + test.rem_disks_nm.items())
        
            if len(disks_all) > 0:
                print "Found the following mounted %s partitions:" % args.device

                for k,v in disks_all.iteritems():
                    print "%s : %s" % (k, v)

                print '-' * 20
                print "Running %s file transfer test for %s iterations" % (args.device, args.count)
                
                try: 
                    for i in range(args.count):
                        test.generate_test_data(args.size)
                        parent_hash = test.md5_hash_file(test.tfile.name)
                        print "Parent hash is: %s" % parent_hash
                        for k,v in disks_all.iteritems():
                            print "Copying %s to %s" % (test.tfile.name, v)
                            if not test.copy_file(test.tfile.name, v):
                                errors += 1
                                continue
                            print "Hashing copy on %s" % v
                            target = ''.join((v,'/',os.path.basename(test.tfile.name)))
                            child_hash = test.md5_hash_file(target)
                            print "Hash of %s on %s is %s" % (target, v, child_hash)
                            if not test.compare_hash(parent_hash,child_hash):
                                print "[Iteration %s] Failure on file copy to %s" % (i, k)
                                errors += 1
                            test.clean_up(target)
                        test.clean_up(test.tfile.name)

                finally:
                    if( len(test.rem_disks_nm) > 0 ):
                        if test.umount() != 0:
                            errors += 1
                        test.clean_tmp_dir()

                if errors > 0:
                    print "Completed %s test iterations, but there were errors" % args.count
                    return 1
                else:
                    print "Successfully completed %s %s file transfer test iterations" % (args.count, args.device)
                    return 0
            else:
                print "No device being mounted successfully for testing, aborting"
                return 1
                   
    else:  #If we don't have removable drives attached and mounted
        print "No removable drives were detected, aborting"
        return 1

if __name__ == '__main__':
    sys.exit(main())
