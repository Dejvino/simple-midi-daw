import time
import subprocess
from threading import Thread
import mido

from .appservice import AppService
from .midi import MidiEvent

class Synth(AppService):
    def __init__(self, inbox):
        super().__init__(inbox)

    def startup(self):
        synth_name = "FLUID Synth"
        self.synth = spawn_synth()
        portname = None
        for name in mido.get_output_names():
            if name.find(synth_name) != -1:
                portname = name
        if portname == None:
            print(f"FATAL: Could not find synth port '{synth_name}'.")
            self.deliver_message("exit")
            return
        self.synth_port = mido.open_output(portname)

    def shutdown(self):
        self.synth.terminate()

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
        self.synth_port.send(m)

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth
