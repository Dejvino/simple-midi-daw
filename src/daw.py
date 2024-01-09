from .midi import create_client, create_output_port, find_keyboard_port, send_note_on, send_note_off, send_sysex
from .appconfig import load_common, load_keyboards
from .appservice import AppService

class Daw(AppService):
    def __init__(self, dawInbox, kbdInbox):
        super().__init__(dawInbox)
        self.kbdInbox = kbdInbox

    def startup(self):
        pass

    def shutdown(self):
        pass

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in DAW: " + repr(msg))
    