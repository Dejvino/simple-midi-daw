from .midi import create_client
from .appconfig import load_common, load_keyboards
from .appservice import AppService

class Daw(AppService):
    def __init__(self, dawInbox):
        super().__init__(dawInbox)

    def startup(self):
        self.client = create_client("daw")
        self.enter_daw_mode()

    def shutdown(self):
        self.leave_daw_mode()

    def enter_daw_mode(self):
        # TODO: enable DAW in all recognized and supported kbds
        #for_every_keyboard(send_note_on())
        pass

    def leave_daw_mode(self):
        # TODO: leave DAW in previously registered kbds
        pass

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in DAW: " + repr(msg))
            
