import sys, traceback
import subprocess
from threading import Thread
import time

from .appservice import AppServiceInbox
from .appservices import AppServices, wrap_runnable_in_thread
from .eventlistener import EventListener
from .daw import Daw
from .metronome import Metronome
from .playback import Playback
from .recorder import Recorder
from .midikeyboard import MidiKeyboard
from .synth import Synth

def run_services():
    app_services = AppServices()

    # App starting...
    dawInbox = AppServiceInbox()
    synthInbox = AppServiceInbox()
    metronomeInbox = AppServiceInbox()
    playbackInbox = AppServiceInbox()
    recorderInbox = AppServiceInbox()
    kbdInbox = AppServiceInbox()

    app_services.add_aux_service(Daw(dawInbox, kbdInbox, synthInbox, metronomeInbox, playbackInbox, recorderInbox))
    app_services.add_aux_service(Metronome(metronomeInbox, synthInbox, dawInbox))
    app_services.add_aux_service(Playback(playbackInbox, dawInbox, synthInbox))
    app_services.add_aux_service(Recorder(recorderInbox))
    app_services.add_aux_service(MidiKeyboard(kbdInbox))
    app_services.add_aux_service(Synth(synthInbox))

    eventListener = EventListener(dawInbox)
    try:
        # app running:        
        app_services.run_main_service(eventListener)
        # ...app terminating.
    except KeyboardInterrupt:
        print("Keyboard interrupt.")
    except Exception as e:
        print("Exception in main thread: ", e)
    finally:
        print("Exiting...")
        app_services.send_aux_message("exit")
    
    app_services.wait_for_aux_services()
    # app terminated.

def app(args):
    run_services()
        
def main():
    import argparse

    services = ["metronome", "playback", "daw", "keyboard", "synth"]
    parser = argparse.ArgumentParser(description='Simple MIDI DAW')
    parser.add_argument('-s', '--standalone', choices=services,
                        help='component to run in standalone mode, without the whole DAW')

    args = parser.parse_args()
    
    if args.standalone:
        import code
        inbox = AppServiceInbox()
        match args.standalone:
            case "metronome":
                service = Metronome(inbox)
            case "playback":
                service = Playback(inbox)
            case "daw":
                service = Daw(inbox)
            case "keyboard":
                service = MidiKeyboard(inbox)
            case "synth":
                service = Synth(inbox)
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
