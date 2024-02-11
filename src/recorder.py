import subprocess
from threading import Thread
import mido
import random
import sys
import time
from mido import MAX_PITCHWHEEL, Message, MidiFile, MidiTrack

from .midi import ActiveNotesTracker
from .appservice import AppService, AppServiceInbox
from .appservices import AppServiceThread
from .midi import MidiEvent
from .metronome import MetronomeTick

class RecorderMsg:
    def __init__(self, operation, channel=None, file=None):
        self.operation = operation
        self.channel = int(channel)
        self.file = file

class Recorder(AppService):
    def __init__(self, inbox):
        super().__init__(inbox)
        self.file = None
        self.recording = False
        self.timer_last = time.time()
        self.ticks_per_beat = 480
        self.recording_scheduled = False
        self.stop_scheduled = False
        self.active_notes_tracker = None

    def startup(self):
        pass
    
    def tick(self):
        pass

    def on_message(self, msg):
        #print("Message in record: " + repr(msg))
        if isinstance(msg, RecorderMsg):
            op = msg.operation
            if (op == "record"):
                self.on_record(msg.file)
            elif (op == "stop"):
                self.on_stop()
            else:
                print("Unknown record message op: " + op)
        elif isinstance(msg, MidiEvent):
            if self.active_notes_tracker != None:
                self.active_notes_tracker.consume_midi_event(msg.event)
            if self.recording:
                self.record_midi_event(msg.event)
        elif isinstance(msg, MetronomeTick):
            if msg.current_beat == 0:
                if self.recording_scheduled:
                    self.record_start()
                if self.stop_scheduled:
                    self.record_stop()
        else:
            print("Unknown record message: " + repr(msg))
        
    def on_record(self, file):
        print(f"Record: REC ({file})")
        self.file = file
        self.recording_scheduled = True
        self.active_notes_tracker = ActiveNotesTracker()

    def on_stop(self):
        print("Record: STOP")
        self.stop_scheduled = True

    def record_start(self):
        self.recording_scheduled = False
        if self.recording == True:
            print("Recorder already recording")
            return
        self.recording = True
        self.midifile = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        self.track = MidiTrack()
        self.midifile.tracks.append(self.track)
        self.timer_diff()
        if self.active_notes_tracker != None:
            active_notes = self.active_notes_tracker.get_active_notes()
            for note in active_notes:
                self.record_midi_event(active_notes[note])
        print("Record start: ", self.file)

    def record_stop(self):
        self.stop_scheduled = False
        if self.recording != True:
            print("Recorder not recording yet")
            return
        if self.active_notes_tracker != None:
            note_offs = self.active_notes_tracker.get_note_offs()
            for note in note_offs:
                self.record_midi_event(note_offs[note])
            self.active_notes_tracker = None
        self.record_midi_event(mido.MetaMessage("end_of_track"))
        self.recording = False
        self.midifile.save(self.file)
        
    def record_midi_event(self, event):
        time_diff = self.timer_diff()
        event.time = int((time_diff * 1000))
        # cut "a bit" from the end to enable looping
        # TODO: make less hacky
        if event.type == "end_of_track":
            event.time = max(0, event.time - self.ticks_per_beat // 4)
        #print("REC:", repr(event))
        self.track.append(event)

    def timer_diff(self):
        timer_now = time.time()
        timer_last = self.timer_last
        self.timer_last = timer_now
        return timer_now - timer_last
