import sys, traceback
import subprocess
from threading import Thread
import time

from .midi import connect_keyboard_to_synth, connect_port_to_synth, connect_to_every_keyboard, send_note, create_client, create_output_port, create_input_port 
from .appconfig import load_common

def wrap_runnable(fn):
    try:
        fn()
    except Exception as e:
        print("EXCEPTION: " + str(e))
        traceback.print_exc(file=sys.stdout)

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth

def event_listener():
    client = create_client("listener")
    connect_to_every_keyboard(client)
    while True:
            event = client.event_input()
            # TODO: handle events
            print(repr(event))

def metronome():
    config = load_common()['metronome']
    client = create_client("metronome")
    port = create_output_port(client)
    connect_port_to_synth(client, port)

    enabled = config.getboolean("enabled")
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
        # TODO: enable/disable controlled by MIDI keyboard
        if enabled:
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


def run_metronome_and_listnener():
    listenerThread = Thread(target=lambda : wrap_runnable(event_listener))
    listenerThread.start()
    time.sleep(1)
    metronomeThread = Thread(target=lambda : wrap_runnable(metronome))
    metronomeThread.start()
    
    listenerThread.join()
    metronomeThread.join()

def main():
    with spawn_synth() as synth:
        connect_keyboard_to_synth()
        run_metronome_and_listnener()
        synth.terminate()
