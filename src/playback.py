import time
import subprocess
from threading import Thread
import mido
import traceback, sys

from .appservice import AppService, AppServiceInbox
from .appservices import AppServiceThread
from .midi import MidiEvent, ActiveNotesTracker
from .metronome import MetronomeTick

class PlaybackMsg:
    def __init__(self, operation, channel):
        self.operation = operation
        self.channel = int(channel)

class Playback(AppService):
    def __init__(self, inbox, dawInbox, synthInbox):
        super().__init__(inbox)
        self.dawInbox = dawInbox
        self.synthInbox = synthInbox
        self.file = "recording.mid"
        self.play_threads = {}
        self.looping = False

    def startup(self):
        pass
    
    def shutdown(self):
        self.try_play_thread_stop()

    def tick(self):
        pass

    def on_message(self, msg):
        #print("Message in playback: " + repr(msg))
        if isinstance(msg, PlaybackMsg):
            op = msg.operation
            if (op == "play"):
                self.on_play(msg)
            elif (op == "stop"):
                self.on_stop(msg)
            elif (op == "loop"):
                self.on_loop(msg)
            elif op in ["play_done", "loop_done"]:
                self.on_thread_done(msg)
            elif op in ["play_stopped", "play_started", "play_paused", "loop_stopped", "loop_started", "loop_paused"]:
                self.report_up(msg)
            else:
                print("Unknown playback message operation: " + repr(op))
        elif isinstance(msg, MetronomeTick):
            if msg.current_beat == 0:
                for thread in self.play_threads.values():
                    thread.service.inbox.put("play_if_paused")
                
        else:
            print("Unknown playback message: " + repr(msg))
        
    def on_play(self, msg):
        print("Playback: PLAY")
        self.start_play_thread(channel=msg.channel)

    def on_stop(self, msg):
        print("Playback: STOP")
        self.try_play_thread_stop(channel=msg.channel)

    def on_loop(self, msg):
        self.looping = not self.looping
        print("Playback: LOOP", self.looping)
        if self.looping:
            self.start_play_thread(channel=msg.channel, loop=True)

    def on_thread_done(self, msg):
        done_threads = []
        for key, thread in self.play_threads.items():
            if not thread.is_alive():
                thread.join()
                done_threads.append(key)
                self.report_up("play_stopped", channel=key)
        for done_thread in done_threads:
            del self.play_threads[done_thread]

    def try_play_thread_stop(self, channel=None):
        if channel == None:
            for thread in self.play_threads.values():
                print("Playback stopping player.")
                thread.deliver_message("exit")
            for thread in self.play_threads.values():
                thread.join()
                print("Playback player finished.")
            self.play_threads = {}
        else:
            if channel in self.play_threads:
                thread = self.play_threads[channel]
                thread.deliver_message("exit")
                thread.join()
                del self.play_threads[channel]
                self.report_up("play_stopped", channel=channel)

    def start_play_thread(self, channel, loop=False):
        # TODO: limit to one thread per measure
        thread = AppServiceThread(PlayerService(AppServiceInbox(), self.file, self.synthInbox, self.inbox, channel, loop=loop))
        thread.start()
        self.play_threads[channel] = thread

    def report_up(self, operation, channel=None):
        if isinstance(operation, PlaybackMsg):
            msg = operation
        else:
            msg = PlaybackMsg(operation, channel)
        self.dawInbox.append(msg)

class PlayerService(AppService):
    def __init__(self, inbox, file, synthInbox, playerInbox, channel, loop=False):
        super().__init__(inbox, blocking=False)
        self.file = file
        self.synthInbox = synthInbox
        self.playerInbox = playerInbox
        self.paused = True
        self.channel = channel
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
        self.report_up("done")
         
    def tick(self):
        if self.paused:
            return
        # TODO: tolerance?
        if time.time() + 0.025 < self.next_note_time:
            time.sleep(0)
            return
        try:
            timeout = 0
            message = self.next_note
            while timeout == 0:
                if message and not isinstance(message, mido.MetaMessage):
                    message.channel = self.channel
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
        self.report_up("started")
        self.play_started = time.time()
        self.play_ending = self.play_started + self.play_length
        self.active_notes_tracker = ActiveNotesTracker()
        self.play = self.play_midi()
        print("Player playback start: ", self.file)

    def play_stop(self):
        self.paused = True
        self.report_up("paused")
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

    def report_up(self, operation):
        op = ("loop" if self.loop else "play") + "_" + operation
        self.playerInbox.append(PlaybackMsg(op, channel=self.channel))
