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
        sound_file = os.path.join(SHARE_DIR, "gui", "sound.wav")
        gnome.sound_play(sound_file)

        try:
            fd = file('/proc/asound/card0/id')
            device = fd.readline().strip()
        except IOError:
            device = 'None'

        return device

    def action_resolution(self):
        ati_brain_damage = []
        command = 'xrandr -q'
        for item in os.popen('lsmod | grep fglrx'):
            ati_brain_damage.append(item)

        if len(ati_brain_damage):
            retval = "impossible with fglrx"
        else:
           for line in os.popen(command):
              fields = string.splitfields(line, '  ')
              if fields[0].startswith('*'):
                 freq = fields[4].strip('*')
                 if fields[4].strip('*') == '\n':
                     freq = "N/A"
                 retval = fields[1] + " @ " + freq + " Hz"

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


def execute(name):
    result = ''
    action = Action()
    action_name = 'action_%s' % name
    if hasattr(action, action_name):
        result = getattr(action, action_name)()
    return result
