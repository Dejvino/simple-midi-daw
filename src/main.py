import sys, traceback
import subprocess
from threading import Thread
import time
from collections import deque

from alsa_midi import WRITE_PORT
from .midi import subscribe_keyboards_to_synth, connect_port_to_synth, connect_to_every_keyboard, send_note, create_client, create_output_port, create_input_port, for_every_keyboard
from .appconfig import load_common

def wrap_runnable_in_thread(runnable):
    def wrapper():
        try:
            print("Thread running")
            runnable.run()
        except Exception as e:
            print("EXCEPTION: " + str(e))
            traceback.print_exc(file=sys.stdout)

    return Thread(target=wrapper)

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth

class EventListener:
    def __init__(self, metronomeInbox):
        self.metronomeInbox = metronomeInbox

    def run(self):    
        client = create_client("listener")
        # TODO: move to midi.py
        port = client.create_port("midiIn", WRITE_PORT)
        for_every_keyboard(lambda kbd_port : client.subscribe_port(kbd_port, port))
        while True:
                event = client.event_input()
                self.on_event(event)
    
    def on_event(self, event):
        # TODO: check event
        print("Event in listener: " + repr(event))
        if (event.value > 60):
            self.metronomeInbox.append("click")

class Metronome:
    def __init__(self, inbox):
        self.inbox = inbox

    def run(self):
        config = load_common()['metronome']
        client = create_client("metronome")
        port = create_output_port(client)
        connect_port_to_synth(client, port)

        self.enabled = config.getboolean("enabled")
        bpm = int(config['bpm'])
        beat_primary_note = config['beat_primary_note']
        beat_primary_velocity = config['beat_primary_velocity']
        beat_secondary_note = config['beat_secondary_note']
        beat_secondary_velocity = config['beat_secondary_velocity']
        beat_time = config['beat_time'].split("/")
        beat_time_beats = int(beat_time[0])
        beat_time_measure = int(beat_time[1])
        channel = config['channel']
        current_beat = 0
        while True:
            self.check_inbox()
            if self.enabled:
                print("Tick {}/{}".format(current_beat+1, beat_time_measure))
                wait = 60 / bpm
                try:
                    if current_beat == 0:
                        send_note(client, port, channel, beat_primary_note, beat_primary_velocity, wait)
                    else:
                        send_note(client, port, channel, beat_secondary_note, beat_secondary_velocity, wait)
                except:
                    print("EXCEPTION sending metronome note. Exiting.")
                    raise
            current_beat = (current_beat + 1) % beat_time_measure

    def check_inbox(self):
        while self.inbox:
            msg = self.inbox.popleft()
            self.on_message(msg)
    
    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in metronome: " + repr(msg))
        self.enabled = not self.enabled

def run_metronome_and_listnener():
    metronomeInbox = deque()

    eventListener = EventListener(metronomeInbox)
    eventListenerThread = wrap_runnable_in_thread(eventListener)
    eventListenerThread.start()
    
    time.sleep(1)
    
    metronome = Metronome(metronomeInbox)
    metronomeThread = wrap_runnable_in_thread(metronome)
    metronomeThread.start()
    
    eventListenerThread.join()
    metronomeThread.join()

def main():
    with spawn_synth() as synth:
        subscribe_keyboards_to_synth()
        run_metronome_and_listnener()
        synth.terminate()
