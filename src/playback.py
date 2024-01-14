import subprocess
from threading import Thread
import mido

from .appservice import AppService, AppServiceInbox
from .appservices import AppServiceThread
from .midi import MidiEvent
from .metronome import MetronomeTick

class Playback(AppService):
    def __init__(self, inbox, synthInbox):
        super().__init__(inbox)
        self.synthInbox = synthInbox
        self.file = "recording.mid"
        self.play_thread = None

    def startup(self):
        pass
    
    def shutdown(self):
        self.try_play_thread_stop()

    def tick(self):
        pass

    def on_message(self, msg):
        #print("Message in playback: " + repr(msg))
        if isinstance(msg, str):
            if (msg == "play"):
                self.on_play()
            elif (msg == "stop"):
                self.on_stop()
            elif (msg == "loop"):
                self.on_loop()
            elif (msg == "play_done"):
                if self.play_thread != None and not self.play_thread.is_alive():
                    self.play_thread.join()
                    self.play_thread = None
            else:
                print("Unknown playback message: " + repr(msg))
        elif isinstance(msg, MetronomeTick):
            if msg.current_beat == 0 and self.play_thread != None:
                self.play_thread.service.inbox.put("play_if_paused")
                
        else:
            print("Unknown playback message: " + repr(msg))
        
    def on_play(self):
        print("Playback: PLAY")
        self.start_play_thread()

    def on_stop(self):
        print("Playback: STOP")
        self.try_play_thread_stop()

    def on_loop(self):
        print("Playback: LOOP")
        self.start_play_thread(loop=True)

    def try_play_thread_stop(self):
        if self.play_thread != None:
            self.play_thread.deliver_message("exit")
            self.play_thread.join()
            self.play_thread = None

    def start_play_thread(self, loop=False):
        if self.play_thread == None:
            self.play_thread = AppServiceThread(PlayerService(AppServiceInbox(), self.file, self.synthInbox, self.inbox, loop=loop))
            self.play_thread.start()

    # TODO: add somethere, e.g. Undo?
    #send_panic_event_to_synth()

class PlayerService(AppService):
    def __init__(self, inbox, file, synthInbox, playerInbox, loop=False):
        super().__init__(inbox, blocking=False)
        self.file = file
        self.synthInbox = synthInbox
        self.playerInbox = playerInbox
        self.paused = True
        self.loop = loop

    def startup(self):
        self.midifile = mido.MidiFile(self.file)

    def shutdown(self):
        print("Playback done: ", self.file)
        self.playerInbox.put("play_done")
         
    def tick(self):
        if self.paused:
            return
        try:
            message = next(self.play)
            self.synthInbox.put(MidiEvent("midi", message))
        except StopIteration:
            if self.loop:
                self.paused = True
            else:
                self.inbox.put("exit")

    def on_message(self, msg):
        if msg == "play_if_paused":
            self.play_if_paused()
        
    def play_if_paused(self):
        if not self.paused:
            return
        self.play_start()
        print("Playback start: ", self.file)

    def play_start(self):
        self.paused = False
        self.play = self.midifile.play()