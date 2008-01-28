from gettext import gettext as _

from hwtest.plugin import Plugin


class IntroPrompt(Plugin):

    def register(self, manager):
        super(IntroPrompt, self).register(manager)
        self._manager.reactor.call_on(("prompt", "intro"), self.prompt_intro)

    def prompt_intro(self, interface):
        interface.show_intro(_("Welcome to Hardware Testing!"),
            _("""\
This application will gather information from your hardware. Then,
you will be asked questions to confirm that the hardware is working
properly. Finally, you will be asked for the e-mail address you use
to sign in to Launchpad in order to submit the information and your
answers.

If you do not have a Launchpad account, please register here:

  https://launchpad.net/+login

Thank you for taking the time to test your hardware."""))


factory = IntroPrompt
