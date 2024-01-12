
import subprocess
from threading import Thread
import fluidsynth

from .appservice import AppService
from .eventlistener import MidiEvent

class Synth(AppService):
    def __init__(self, inbox):
        super().__init__(inbox)

    def startup(self):
        fs = fluidsynth.Synth()
        self.synth = fs
        fs.start()
        self.sfid = sfid = fs.sfload("default.sf2")
        fs.program_select(0, sfid, 0, 0)

    def shutdown(self):
        self.synth.delete()

    def on_message(self, msg):
        if isinstance(msg, MidiEvent):
            m = msg.event
            self.synth.noteon(chan=m.channel-1, key=m.note, vel=m.velocity)
        else:
            print("Unknown synth message: " + repr(msg))