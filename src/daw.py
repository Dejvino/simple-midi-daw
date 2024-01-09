from .midi import create_client, create_output_port, find_keyboard_port, send_note_on, send_note_off, send_sysex
from .appconfig import load_common, load_keyboards
from .appservice import AppService

class Daw(AppService):
    def __init__(self, dawInbox):
        super().__init__(dawInbox)

    def startup(self):
        self.connect_keyboard()

    def shutdown(self):
        self.disconnect_keyboard()

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in DAW: " + repr(msg))
            
    def connect_keyboard(self):
        pass
        # TODO

    def disconnect_keyboard(self):
        pass
        # TODO
