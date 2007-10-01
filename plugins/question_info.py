import os
import re
import gnome

from hwtest.pci import get_pci_devices
from hwtest.pci_ids import get_class, get_device
from hwtest.plugin import Plugin
from hwtest.excluder import Excluder
from hwtest.question import Question, QuestionManager
from hwtest.constants import HWTEST_DIR


TEST_DOMAIN = "canonical.com"


class QuestionRepository(object):

    def __init__(self):
        self.devices = get_pci_devices()
        self.questions = [Question(**kwargs) for kwargs in [
            {"name": "audio",
             "cats": ["laptop", "desktop"],
             "command": self.command_audio,
             "desc": """\
Testing detected soundcard:

$result

Did you hear a sound?"""},
            {"name": "resolution",
             "cats": ["laptop", "desktop"],
             "command": self.command_resolution,
             "desc": """\
Testing detected resolution:

$result

Is your video display hardware working properly?"""},
            {"name": "mouse",
             "cats": ["laptop", "desktop"],
             "desc": """\
Moving the mouse should move the cursor on the screen.

Is your mouse working properly?"""},
            {"name": "network",
             "command": self.command_network,
             "desc": """\
Detecting your network controller(s):

$result

Is this correct?"""},
            {"name": "internet",
             "command": self.command_internet,
             "desc": """\
Testing your internet connection:

$result

Is your internet connection working properly?"""},
            {"name": "keyboard",
             "desc": """\
Typing keys on your keyboard should display the corresponding
characters in a text area.

Is your keyboard working properly?"""}]]

    def command_audio(self):
        print 'here'
        gnome.sound_init("localhost")
        sound_file = os.path.join(HWTEST_DIR, "data", "sound.wav")
        gnome.sound_play(sound_file)

        try:
            fd = file('/proc/asound/card0/id')
            device = fd.readline().strip()
        except IOError:
            device = 'None'

        print 'there'
        return device

    def command_resolution(self, test_output=None):
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

    def command_network(self):
        network_devices = filter(
            lambda x: get_class(x["class_name"]) == "Network controller",
            self.devices)
        network_strings = map(
            lambda x: get_device(x["vendor"], x["device"]),
            network_devices)
        return "\n".join(network_strings)

    def command_internet(self):
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


class QuestionInfo(Plugin):

    def __init__(self, question_manager=None):
        super(QuestionInfo, self).__init__()
        question_manager = question_manager or QuestionManager()
        question_repository = QuestionRepository()
        for question in question_repository.questions:
            question_manager.add(question)
        self.questions = question_manager.get_iterator()
        self.question = self.questions.next()

    def register(self, manager):
        self._manager = manager
        self._manager.reactor.call_on("run", self.run, -200)
        self._manager.reactor.call_on(("question", "category"), self.set_category)
        self._manager.reactor.call_on(("question", "direction"), self.set_direction)

    def run(self):
        while self.question:
            self._manager.reactor.fire(("interface", "question"),
                self.question, self.questions.has_prev(),
                self.questions.has_next())

    def exchange(self):
        # TODO: gather question information
        pass

    def set_category(self, category):
        exclude_func = lambda question, c=category: c not in question.categories
        self.questions = iter(Excluder(self.questions, exclude_func, exclude_func))
        self.question = self.questions.next()

    def set_direction(self, direction):
        questions = self.questions
        if direction is 1:
            self.question = questions.has_next() and questions.next() or None
        else:
            self.question = questions.has_prev() and questions.prev() or None


factory = QuestionInfo
