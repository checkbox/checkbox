#!/usr/bin/python3

import re
import os
import sys
import time
import shutil
import tempfile
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from argparse import ArgumentParser


class URLLister(HTMLParser):
    """HTML parser to find the desired cloud image hyperlink
    """

    def __init__(self, url):
        HTMLParser.__init__(self)
        self.url = None
        self.feed(urllib.request.urlopen(url).read().decode())

    def handle_starttag(self, tag, attrs):
        if tag == 'a' and attrs:
            for k, v in attrs:
                if k == 'href' and re.search('i386.*img$', v):
                    self.url = v


class KVM():
    """Creates an object to handle the actions necessary for KVM testing.
    """

    def __init__(self, image_file):
        self.max_retries = 4
        self.kvm_process = None
        self.public_key = None
        self.cloud_image = image_file
        self.test_state = 1

    def _setup(self):
        if not self.cloud_image:
            return self.test_state

        self.vm_dir = tempfile.mkdtemp(dir='/tmp')

        if not os.path.isfile(self.cloud_image):
            try:
                subprocess.check_call(
                    ['wget', self.cloud_image],
                    cwd=self.vm_dir,
                    stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
                self.cloud_image = os.path.basename(self.cloud_image)
            except subprocess.CalledProcessError:
                return self.test_state

        # Create public/private ssh keus for passwordless auth.
        try:
            subprocess.check_call(
                "ssh-keygen -q -t rsa -f %s -N '' -C ''"
                % os.path.join(self.vm_dir, 'ssh_key'),
                cwd=self.vm_dir, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            return self.test_state

        with open(os.path.join(self.vm_dir, 'ssh_key.pub'), 'r') as f:
            self.public_key = '\n'.join(f.readlines())

        # Create user-data and meta-data files that will be used to modify
        # image on first boot
        with open(os.path.join(self.vm_dir, 'meta-data'), 'w') as f:
            f.write('\n'.join([
                    'instance-id: iid-local01',
                    'local-hostname: cloudimg']))

        with open(os.path.join(self.vm_dir, 'user-data'), 'w') as f:
            f.write('\n'.join([
                    '#cloud-config',
                    'password: passw0rd',
                    'chpasswd: { expire: False }',
                    'ssh_pwauth: True',
                    'ssh_authorized_keys:',
                    ' - %s' % self.public_key]))

        # create a disk to attach with some user-data and meta-data
        try:
            subprocess.check_call([
                'genisoimage',
                '-output', 'seed.iso',
                '-volid', 'cidata',
                '-joliet',
                '-rock',
                'user-data', 'meta-data'],
                cwd=self.vm_dir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            return self.test_state

        # create a new qcow image to boot, backed by the original image
        try:
            subprocess.check_call([
                'qemu-img', 'create',
                '-f', 'qcow2',
                '-b', self.cloud_image,
                'boot-disk.img'],
                cwd=self.vm_dir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except subprocess.CalledProcessError:
            return self.test_state

    def _teardown(self):
        if self.kvm_process:
            self.kvm_process.terminate()
        shutil.rmtree(self.vm_dir)

    def run(self):
        self._setup()

        # Boot the image
        self.kvm_process = subprocess.Popen([
            'kvm', '-m', '256', '-net', 'nic', '-net',
            'user,net=10.0.0.0/8,host=10.0.0.1,hostfwd=tcp::2222-:22',
            '-drive', 'file=boot-disk.img,if=virtio',
            '-drive', 'file=seed.iso,if=virtio',
            '-display', 'none'],
            cwd=self.vm_dir,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        # Verify that the VM is running
        for i in range(self.max_retries):
            time.sleep(30)
            (status, output) = subprocess.getstatusoutput(' '.join([
                'ssh -q -p 2222',
                '-o StrictHostKeyChecking=no',
                '-o UserKnownHostsFile=/dev/null',
                '-o Batchmode=yes',
                '-o ConnectTimeout=5',
                '-i %s' % os.path.join(self.vm_dir, 'ssh_key'),
                'ubuntu@127.0.0.1',
                'echo TEST_SUCCESS']))
            if not status and output == 'TEST_SUCCESS':
                self.test_state = 0
                break

        self._teardown()
        return self.test_state


def get_released_latest():
    """Get the latest stable release of server-cloudimg available from
       http://cloud-images.ubuntu.com
    """
    releases = urllib.request.urlopen(
        "http://cloud-images.ubuntu.com/query/released.latest.txt").read()
    releases = re.sub("\n+$", "", releases.decode(), re.S).split("\n")

    rel = [re.sub("\s.*", "", x) for x in releases if 'release' in x][-1]
    base = "http://cloud-images.ubuntu.com/%s/current/" % rel
    parser = URLLister(base)
    return base + parser.url


def main():
    parser = ArgumentParser("Check that a VM boots and works with KVM")
    parser.add_argument("CLOUD_IMAGE",
        nargs='?',
        default=get_released_latest(),
        help="Cloud image used to boot the virtual machine")

    args = parser.parse_args()
    kvm_test = KVM(args.CLOUD_IMAGE)
    return kvm_test.run()

if __name__ == '__main__':
    sys.exit(main())
