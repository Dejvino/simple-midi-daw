import time
import subprocess
from threading import Thread
import mido
import traceback, sys

from .appservice import AppService, AppServiceInbox
from .appservices import AppServiceThread
from .midi import MidiEvent, ActiveNotesTracker
from .metronome import MetronomeTick

class Playback(AppService):
    def __init__(self, inbox, synthInbox):
        super().__init__(inbox)
        self.synthInbox = synthInbox
        self.file = "recording.mid"
        self.play_threads = []
        self.looping = False

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
                self.on_thread_done()
                    
            else:
                print("Unknown playback message: " + repr(msg))
        elif isinstance(msg, MetronomeTick):
            if msg.current_beat == 0:
                for thread in self.play_threads:
                    thread.service.inbox.put("play_if_paused")
                
        else:
            print("Unknown playback message: " + repr(msg))
        
    def on_play(self):
        print("Playback: PLAY")
        self.start_play_thread()

    def on_stop(self):
        print("Playback: STOP")
        self.try_play_thread_stop()

    def on_loop(self):
        self.looping = not self.looping
        print("Playback: LOOP", self.looping)
        if self.looping:
            self.start_play_thread(loop=True)

    def on_thread_done(self):
        done_threads = []
        for thread in self.play_threads:
            if not thread.is_alive():
                thread.join()
                done_threads.append(thread)
        for done_thread in done_threads:
            self.play_threads.remove(done_thread)

    def try_play_thread_stop(self):
        for thread in self.play_threads:
            print("Playback stopping player.")
            thread.deliver_message("exit")
        for thread in self.play_threads:
            thread.join()
            print("Playback player finished.")
        self.play_threads = []

    def start_play_thread(self, loop=False):
        # TODO: limit to one thread per measure
        thread = AppServiceThread(PlayerService(AppServiceInbox(), self.file, self.synthInbox, self.inbox, loop=loop))
        thread.start()
        self.play_threads.append(thread)

class PlayerService(AppService):
    def __init__(self, inbox, file, synthInbox, playerInbox, loop=False):
        super().__init__(inbox, blocking=False)
        self.file = file
        self.synthInbox = synthInbox
        self.playerInbox = playerInbox
        self.paused = True
        self.loop = loop
        self.ticks_per_beat = 480
        self.active_notes_tracker = None
        self.next_note = None
        self.next_note_time = time.time()
        self.play_started = None
        self.play_ending = None
        self.play_length = None

    def startup(self):
        try:
            self.midifile = mido.MidiFile(self.file, ticks_per_beat=self.ticks_per_beat)
            self.play_length = self.midifile.length
        except Exception as e:
            print("Player error:", str(e))
            traceback.print_exc(file=sys.stdout)
            self.inbox.put("exit")

    def shutdown(self):
        self.play_stop()
        print("Playback done: ", self.file)
        self.playerInbox.put("play_done")
         
    def tick(self):
        if self.paused:
            return
        # TODO: tolerance?
        if time.time() + 0.1 < self.next_note_time:
            return
        try:
            timeout = 0
            message = self.next_note
            while timeout == 0:
                if message and not isinstance(message, mido.MetaMessage):
                    self.active_notes_tracker.consume_midi_event(message)
                    self.synthInbox.put(MidiEvent("midi", message))
                self.next_note_time, message = next(self.play)
                timeout = message.time
            self.next_note = message
        except StopIteration:
            if self.loop:
                self.play_stop()
                print("Player finished. Looping, waiting.")
            else:
                self.play_stop()
                print("Player finished. Stopping.")
                self.active = False

    def on_message(self, msg):
        if msg == "play_if_paused":
            self.play_if_paused()
        
    def play_if_paused(self):
        time_now = time.time()
        # TODO: tolerance?
        if self.loop and self.play_ending and self.play_ending - time_now < 1:
            print("Player looping time!")
            self.play_stop()
        if not (self.paused and self.active):
            return
        self.play_start()

    def play_start(self):
        self.paused = False
        self.play_started = time.time()
        self.play_ending = self.play_started + self.play_length
        self.active_notes_tracker = ActiveNotesTracker()
        self.play = self.play_midi()
        print("Player playback start: ", self.file)

    def play_stop(self):
        self.paused = True
        if self.active_notes_tracker != None:
            note_offs = self.active_notes_tracker.get_note_offs()
            for note in note_offs:
                self.synthInbox.put(MidiEvent("midi", note_offs[note]))
            self.active_notes_tracker = None

    def play_midi(self):
        now=time.time
        start_time = now()
        input_time = 0.0

        for msg in self.midifile:
            input_time += msg.time
            yield start_time + input_time, msg