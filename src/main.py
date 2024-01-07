import sys, traceback
import subprocess
from threading import Thread
import time
from collections import deque

from .midi import subscribe_keyboards_to_synth
from .eventlistener import EventListener
from .daw import Daw
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
    # App starting...
    dawInbox = deque()
    metronomeInbox = deque()
    playbackInbox = deque()

    eventListener = EventListener(dawInbox, metronomeInbox, playbackInbox)
    eventListenerThread = wrap_runnable_in_thread(eventListener)
    eventListenerThread.start()

    time.sleep(1)
    
    service_threads = []
    service_threads.append(wrap_runnable_in_thread(Daw(dawInbox)))
    service_threads.append(wrap_runnable_in_thread(Metronome(metronomeInbox)))
    service_threads.append(wrap_runnable_in_thread(Playback(playbackInbox)))

    for thread in service_threads:
        thread.start()

    try:
        # ... app running ...
        eventListenerThread.join()
        # ...app terminating.
    finally:
        dawInbox.append("exit")
        metronomeInbox.append("exit")
        playbackInbox.append("exit")
    
    for thread in service_threads:
        thread.join()
    # app terminated.

def app(args):
    with spawn_synth() as synth:
        # TODO: move to DAW
        subscribe_keyboards_to_synth()
        run_services()
        synth.terminate()
        
def main():
    import argparse

    services = ["metronome", "playback"]
    parser = argparse.ArgumentParser(description='Simple MIDI DAW')
    parser.add_argument('-s', '--standalone', choices=services,
                        help='component to run in standalone mode, without the whole DAW')


    args = parser.parse_args()
    
    if args.standalone:
        import code
        inbox = deque()
        match args.standalone:
            case "metronome":
                service = Metronome(inbox)
            case "playback":
                service = Playback(inbox)
            case _:
                print("Unknown standalone: ", args.standalone)
                return
        thread = wrap_runnable_in_thread(service)
        thread.start()
        code.interact(banner="Simple MIDI DAW - shell for standalone " + args.standalone, local=dict(globals(), **locals()))
        print("Terminating standalone component.")
        inbox.append("exit")
        thread.join()
        print("Exiting.")
    else:
        app(args)
