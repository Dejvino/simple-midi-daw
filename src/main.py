import sys, traceback
import subprocess
from threading import Thread
import time
from collections import deque

from .appservices import AppServices, wrap_runnable_in_thread
from .midi import subscribe_keyboards_to_synth
from .eventlistener import EventListener
from .daw import Daw
from .metronome import Metronome
from .playback import Playback
from .midikeyboard import MidiKeyboard

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth

def run_services():
    app_services = AppServices()

    # App starting...
    dawInbox = deque()
    metronomeInbox = deque()
    playbackInbox = deque()
    kbdInbox = deque()

    eventListener = EventListener(dawInbox, metronomeInbox, playbackInbox)
    app_services.start_main_service(eventListener)
    
    # TODO: remove and fix waiting for init
    time.sleep(1)

    app_services.add_aux_service(Daw(dawInbox, kbdInbox))
    app_services.add_aux_service(Metronome(metronomeInbox))
    app_services.add_aux_service(Playback(playbackInbox))

    try:
        # ... app running ...
        app_services.wait_for_main_service()
        # ...app terminating.
    finally:
        dawInbox.append("exit")
        metronomeInbox.append("exit")
        playbackInbox.append("exit")
    
    app_services.wait_for_aux_services()
    # app terminated.

def app(args):
    with spawn_synth() as synth:
        # TODO: move to DAW
        subscribe_keyboards_to_synth()
        run_services()
        synth.terminate()
        
def main():
    import argparse

    services = ["metronome", "playback", "daw", "keyboard"]
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
            case "daw":
                service = Daw(inbox)
            case "keyboard":
                service = MidiKeyboard(inbox)
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
