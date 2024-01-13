import time
import subprocess
from threading import Thread
import fluidsynth

from .appservice import AppService
from .midi import MidiEvent

class Synth(AppService):
    def __init__(self, inbox):
        super().__init__(inbox)

    def startup(self):
        fs = fluidsynth.Synth()
        self.synth = fs
        fs.start()
        self.sfid = sfid = fs.sfload("default.sf2")

    def shutdown(self):
        self.synth.delete()

    def on_message(self, msg):
        if isinstance(msg, MidiEvent):
            m = msg.event
            try:
                self.on_midi(m)
            except Exception as e:
                print("Synth MIDI Oops: ", e)
        else:
            print("Unknown synth message: " + repr(msg))

    def on_midi(self, m):
        mtype = m.type
        if mtype == "note_on":
            self.synth.noteon(chan=m.channel, key=m.note, vel=m.velocity)
        elif mtype == "program_change":
            self.synth.program_change(chan=m.channel, prg=m.program)