import subprocess
from threading import Thread
import time

from .appconfig import load_keyboards
from .midi import metronome, event_listener, connect_keyboard_to_synth

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth

def run_metronome_and_listnener():
    listenerThread = Thread(target=event_listener)
    listenerThread.start()
    time.sleep(1)
    metronomeThread = Thread(target=metronome)
    metronomeThread.start()
    
    listenerThread.join()
    metronomeThread.join()

def main():
    with spawn_synth() as synth:
        connect_keyboard_to_synth()
        run_metronome_and_listnener()
        synth.terminate()
