import sys, traceback
import subprocess
from threading import Thread
import time
from collections import deque

from .midi import subscribe_keyboards_to_synth
from .eventlistener import EventListener
from .metronome import Metronome
from .playback import Playback

def wrap_runnable_in_thread(runnable):
    def wrapper():
        try:
            print("Thread running")
            runnable.run()
        except Exception as e:
            print("EXCEPTION: " + str(e))
            traceback.print_exc(file=sys.stdout)
    return Thread(target=wrapper)

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth

def run_services():
    metronomeInbox = deque()
    playbackInbox = deque()

    eventListener = EventListener(metronomeInbox, playbackInbox)
    eventListenerThread = wrap_runnable_in_thread(eventListener)
    eventListenerThread.start()
    
    time.sleep(1)
    
    metronome = Metronome(metronomeInbox)
    metronomeThread = wrap_runnable_in_thread(metronome)
    metronomeThread.start()
    
    playback = Playback(playbackInbox)
    playbackThread = wrap_runnable_in_thread(playback)
    playbackThread.start()

    try:
        eventListenerThread.join()
    finally:
        metronomeInbox.append("exit")
        playbackInbox.append("exit")
    
    metronomeThread.join()
    playbackThread.join()

def main():
    with spawn_synth() as synth:
        subscribe_keyboards_to_synth()
        run_services()
        synth.terminate()
