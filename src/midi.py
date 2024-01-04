import subprocess
from threading import Thread
import time
from alsa_midi import SequencerClient, READ_PORT, WRITE_PORT, NoteOnEvent, NoteOffEvent

from .appconfig import load_common, load_keyboards

def create_client(suffix):
    # TODO: extract app name
    return SequencerClient("simple-midi-daw_" + suffix)

def find_synth_port(client):
    # TODO: find the synth based on name
    return client.list_ports(output=True)[0]

def for_every_keyboard(fn):
    keyboardCfg = load_keyboards()
    keyboardClientName = keyboardCfg['description']['client_name']
    keyboardPortName = keyboardCfg['description']['client_port_name']
    client = create_client("keyboard")
    inPorts = client.list_ports(input=True)
    for port in inPorts:
        if port.client_name == keyboardClientName and port.name == keyboardPortName:
            fn(port)

def connect_keyboard_to_synth():
    keyboardCfg = load_keyboards()
    keyboardClientName = keyboardCfg['description']['client_name']
    keyboardPortName = keyboardCfg['description']['client_port_name']
    print("Expected MIDI keyboard: " + keyboardClientName)
    client = create_client("keyboard")
    synthPort = find_synth_port(client)
    for_every_keyboard(lambda port : client.subscribe_port(port, synthPort))

def event_listener():
    client = create_client("listener")
    port = client.create_port("midiIn", WRITE_PORT)
    for_every_keyboard(lambda kbd_port : client.subscribe_port(kbd_port, port))
    while True:
            event = client.event_input()
            # TODO: handle events
            print(repr(event))

def metronome():
    config = load_common()['metronome']
    client = create_client("metronome")
    port = client.create_port("midiOut", READ_PORT)

    synthPort = find_synth_port(client)
    port.connect_to(synthPort)

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

def send_note(client, port, channel, note, velocity, wait):
    event1 = NoteOnEvent(note=note, velocity=velocity, channel=channel)
    client.event_output_buffer(event1)
    client.drain_output()
    time.sleep(wait)
    event2 = NoteOffEvent(note=note, channel=channel)
    client.event_output_buffer(event2)
    client.drain_output()
