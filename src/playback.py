import subprocess
from threading import Thread

from .appservice import AppService

class Playback(AppService):
    def __init__(self, inbox):
        super().__init__(inbox)
        self.file = "recording.mid"

    def startup(self):
        #self.client = create_client("playback")
        pass
    
    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in playback: " + repr(msg))
        if (msg == "play"):
            self.on_play()
        elif (msg == "record"):
            self.on_record()
        elif (msg == "stop"):
            self.on_stop()
        elif (msg == "loop"):
            self.on_loop()
        else:
            print("Unknown playback message: " + repr(msg))
        
    def on_play(self):
        print("Playback: PLAY")

    def on_stop(self):
        print("Playback: STOP")

    def on_record(self):
        print("Playback: REC")

    def on_loop(self):
        print("Playback: LOOP")

    # TODO: add somethere, e.g. Undo?
    #send_panic_event_to_synth()
