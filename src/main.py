import sys, traceback
import subprocess
from threading import Thread
import time

from .appconfig import load_keyboards
from .midi import metronome, event_listener, connect_keyboard_to_synth

def wrap_runnable(fn):
    try:
        fn()
    except Exception as e:
        print("EXCEPTION: " + str(e))
        traceback.print_exc(file=sys.stdout)

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth

def run_metronome_and_listnener():
    listenerThread = Thread(target=lambda : wrap_runnable(event_listener))
    listenerThread.start()
    time.sleep(1)
    metronomeThread = Thread(target=lambda : wrap_runnable(metronome))
    metronomeThread.start()
    
    listenerThread.join()
    metronomeThread.join()

def main():
    with spawn_synth() as synth:
        connect_keyboard_to_synth()
        run_metronome_and_listnener()
        synth.terminate()
