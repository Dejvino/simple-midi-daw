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

class Recorder(AppService):
    def __init__(self, inbox):
        super().__init__(inbox)
        self.file = "recording.mid"
        self.recording = False
        self.timer_last = time.time()
        self.bpm = 120
        self.ticks_per_beat = 4 * self.bpm

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
            if self.recording:
                self.record_midi_event(msg.event)
        else:
            print("Unknown record message: " + repr(msg))
        
    def on_record(self):
        print("Record: REC")
        self.record_start()

    def on_stop(self):
        print("Record: STOP")
        self.record_stop()

    def record_start(self):
        if self.recording == True:
            print("Recorder already recording")
            return
        self.recording = True
        self.midifile = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        self.track = MidiTrack()
        self.midifile.tracks.append(self.track)
        self.timer_diff()
        print("Record start: ", self.file)

    def record_stop(self):
        if self.recording != True:
            print("Recorder not recording yet")
            return
        self.record_midi_event(mido.MetaMessage("end_of_track"))
        self.recording = False
        self.midifile.save(self.file)
        
    def record_midi_event(self, event):
        time_diff = self.timer_diff()
        event.time = int((time_diff * 1000))
        #print("REC:", repr(event))
        self.track.append(event)

    def timer_diff(self):
        timer_now = time.time()
        timer_last = self.timer_last
        self.timer_last = timer_now
        return timer_now - timer_last