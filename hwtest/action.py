import os
import re
import string
import gnome

from hwtest.pci import get_pci_devices
from hwtest.pci_ids import (get_class, get_device)
import gnome.ui

TEST_DOMAIN = "canonical.com"

from hwtest.constants import SHARE_DIR

class Action:
    def __init__(self):
        self.devices = get_pci_devices()

    def action_audio(self):
        gnome.sound_init("localhost")
        sound_file = os.path.join(SHARE_DIR, "data", "sound.wav")
        gnome.sound_play(sound_file)

        try:
            fd = file('/proc/asound/card0/id')
            device = fd.readline().strip()
        except IOError:
            device = 'None'

        return device

    def action_resolution(self, test_output=None):
        ati_brain_damage = []
        command = 'xrandr -q'
        for item in os.popen('lsmod | grep fglrx'):
            ati_brain_damage.append(item)

        if len(ati_brain_damage):
            retval = "impossible with fglrx"
        else:
            retval = None
            res, freq = None, None
            contents = (test_output or os.popen(command).read()).strip()
            for line in contents.splitlines():
                if line.endswith("*"):
                    # gutsy
                    fields = line.replace("*", "").split()
                    if len(fields) == 2:
                        res, freq = fields
                    else:
                        res, freq = fields[0], "N/A"
                    break
                elif line.startswith("*"):
                    # dapper
                    fields = line.replace("*", "").split('  ')
                    res = fields[1].replace(" ", "")
                    if len(fields) < 4:
                        freq = "N/A"
                    else:
                        freq = fields[4]
                    break

            if res:
                retval = "%s @ %d Hz" % (res, float(freq))

        return retval

    def action_network(self):
        network_devices = filter(
            lambda x: get_class(x["class_name"]) == "Network controller",
            self.devices)
        network_strings = map(
            lambda x: get_device(x["vendor"], x["device"]),
            network_devices)
        return "\n".join(network_strings)

    def action_internet(self):
        command = "ping -q -w4 -c2 %s" % TEST_DOMAIN
        reg = re.compile(r"(\d) received")
        ping = os.popen(command)
        num_packets = 0
        while 1:
            line = ping.readline()
            if not line: break
            received = re.findall(reg, line)
            if received:
                num_packets = int(received[0])

        if num_packets == 0:
            return "No internet connection"
        elif num_packets == 2:
            return "Internet connection fully established"
        else:
            return "Connection established by problematic"


def execute(name, *args):
    result = ''
    action = Action()
    action_name = 'action_%s' % name
    if hasattr(action, action_name):
        result = getattr(action, action_name)(*args)
    return result
