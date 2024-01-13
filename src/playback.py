import subprocess
from threading import Thread
import mido

from .appservice import AppService, AppServiceInbox
from .appservices import AppServiceThread
from .midi import MidiEvent

class Playback(AppService):
    def __init__(self, inbox, synthInbox):
        super().__init__(inbox)
        self.synthInbox = synthInbox
        self.file = "recording.mid"
        self.play_thread = None

    def startup(self):
        pass
    
    def tick(self):
        pass

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in playback: " + repr(msg))
        if (msg == "play"):
            self.on_play()
        elif (msg == "record"):
            self.on_record()
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
        
    def on_play(self):
        print("Playback: PLAY")
        if self.play_thread == None:
            self.play_thread = AppServiceThread(PlayerService(AppServiceInbox(), self.file, self.synthInbox, self.inbox))
            self.play_thread.start()

    def on_stop(self):
        print("Playback: STOP")
        if self.play_thread != None:
            self.play_thread.deliver_message("exit")
            self.play_thread.join()
            self.play_thread = None

    def on_record(self):
        print("Playback: REC")
        import random
        import sys

        from mido import MAX_PITCHWHEEL, Message, MidiFile, MidiTrack

        notes = [64, 64 + 7, 64 + 12]

        outfile = MidiFile()

        track = MidiTrack()
        outfile.tracks.append(track)

        track.append(Message('program_change', program=12))

        delta = 300
        ticks_per_expr = int(sys.argv[1]) if len(sys.argv) > 1 else 20
        for i in range(4):
            note = random.choice(notes)
            track.append(Message('note_on', note=note, velocity=100, time=delta))
            for j in range(delta // ticks_per_expr):
                pitch = MAX_PITCHWHEEL * j * ticks_per_expr // delta
                track.append(Message('pitchwheel', pitch=pitch, time=ticks_per_expr))
            track.append(Message('note_off', note=note, velocity=100, time=0))

        outfile.save(self.file)

    def on_loop(self):
        print("Playback: LOOP")

    # TODO: add somethere, e.g. Undo?
    #send_panic_event_to_synth()

class PlayerService(AppService):
    def __init__(self, inbox, file, synthInbox, playerInbox):
        super().__init__(inbox, blocking=False)
        self.file = file
        self.synthInbox = synthInbox
        self.playerInbox = playerInbox

    def startup(self):
        midifile = mido.MidiFile(self.file)
        self.play = midifile.play()
        print("Playback start: ", self.file)

    def shutdown(self):
        print("Playback done: ", self.file)
        self.playerInbox.put("play_done")
         
    def tick(self):
        print("NOTE")
        try:
            message = next(self.play)
            print("... ", repr(message))
            self.synthInbox.put(MidiEvent("midi", message))
        except StopIteration:
            self.inbox.put("exit")
        