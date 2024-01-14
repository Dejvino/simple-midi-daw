import time
import mido
from .appconfig import load_common
from .appservice import AppService
from .midi import MidiEvent

class Metronome(AppService):
    def __init__(self, inbox, synthInbox):
        super().__init__(inbox, blocking=False)
        self.synthInbox = synthInbox

    def startup(self):
        self.config = config = load_common()['metronome']
        self.enabled = config.getboolean('enabled')
        self.current_beat = 0
        
    def tick(self):
        config = self.config
        bpm = int(config['bpm'])
        beat_primary_note = int(config['beat_primary_note'])
        beat_primary_velocity = int(config['beat_primary_velocity'])
        beat_secondary_note = int(config['beat_secondary_note'])
        beat_secondary_velocity = int(config['beat_secondary_velocity'])
        beat_time = config['beat_time'].split("/")
        beat_time_beats = int(beat_time[0])
        beat_time_measure = int(beat_time[1])
        channel = int(config['channel'])
        wait = 60 / bpm

        if self.enabled:
            #print("Tick {}/{}".format(self.current_beat+1, beat_time_measure))
            wait = 60 / bpm
            try:
                if self.current_beat == 0:
                    self.send_note(channel, beat_primary_note, beat_primary_velocity, wait)
                else:
                    self.send_note(channel, beat_secondary_note, beat_secondary_velocity, wait)
            except:
                print("EXCEPTION sending metronome note. Exiting.")
                raise
        else:
            time.sleep(wait)
        self.current_beat = (self.current_beat + 1) % beat_time_measure

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in metronome: " + repr(msg))
        # TODO: other messages?
        self.enabled = not self.enabled

    def send_note(self, channel, note, velocity, wait):
        self.synthInbox.put(MidiEvent("midi", mido.Message("note_on", note=note, channel=channel, velocity=velocity)))
        time.sleep(wait)
        self.synthInbox.put(MidiEvent("midi", mido.Message("note_off", note=note, channel=channel)))