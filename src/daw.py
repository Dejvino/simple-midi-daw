from .midi import create_client
from .appconfig import load_common, load_keyboards

class Daw:
    def __init__(self, dawInbox):
        self.inbox = dawInbox
        self.active = True

    def run(self):
        self.client = create_client("daw")
        self.enter_daw_mode()
        while self.active:
            self.check_inbox()
        self.leave_daw_mode()

    def enter_daw_mode(self):
        # TODO: enable DAW in all recognized and supported kbds
        #for_every_keyboard(send_note_on())
        pass

    def leave_daw_mode(self):
        # TODO: leave DAW in previously registered kbds
        pass

    def check_inbox(self):
        while self.inbox:
            msg = self.inbox.popleft()
            self.on_message(msg)
    
    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in DAW: " + repr(msg))
        if (msg == "exit"):
            self.active = False
        else:
            print("Unknown DAW message: " + repr(msg))
            
