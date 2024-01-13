import subprocess
from threading import Thread
import mido

from .appservice import AppService
from .midi import MidiEvent

class Playback(AppService):
    def __init__(self, inbox, synthInbox):
        super().__init__(inbox)
        self.synthInbox = synthInbox
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
        midifile = mido.MidiFile(self.file)
        for message in midifile.play():
            self.synthInbox.put(MidiEvent("midi", message))
        print("Playback done")

    def on_stop(self):
        print("Playback: STOP")

    def on_record(self):
        print("Playback: REC")

    def on_loop(self):
        print("Playback: LOOP")

    # TODO: add somethere, e.g. Undo?
    #send_panic_event_to_synth()
