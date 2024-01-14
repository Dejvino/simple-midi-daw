import subprocess
from threading import Thread
import mido
import random
import sys
import time
from mido import MAX_PITCHWHEEL, Message, MidiFile, MidiTrack

from .appservice import AppService, AppServiceInbox
from .appservices import AppServiceThread
from .midi import MidiEvent
from .metronome import MetronomeTick

class Recorder(AppService):
    def __init__(self, inbox):
        super().__init__(inbox)
        self.file = "recording.mid"
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
        # TODO: switch msg type
        #print("Message in record: " + repr(msg))
        if (msg == "record"):
            self.on_record()
        elif (msg == "stop"):
            self.on_stop()
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
        
    def on_record(self):
        print("Record: REC")
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
                note_on = active_notes[note]
                self.record_midi_event(note_on)
        print("Record start: ", self.file)

    def record_stop(self):
        self.stop_scheduled = False
        if self.recording != True:
            print("Recorder not recording yet")
            return
        if self.active_notes_tracker != None:
            active_notes = self.active_notes_tracker.get_active_notes()
            for note in active_notes:
                note_on = active_notes[note]
                note_off = mido.Message("note_off", channel=note_on.channel, note=note_on.note)
                self.record_midi_event(note_off)
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

class ActiveNotesTracker:
    def __init__(self):
        self.notes={}

    def consume_midi_event(self, event):
        if event.note in self.notes:
            del self.notes[event.note]
        else:
            self.notes[event.note] = event

    def get_active_notes(self):
        return self.notes
