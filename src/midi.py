import subprocess
from threading import Thread
import time
from alsa_midi import SequencerClient, READ_PORT, WRITE_PORT, NoteOnEvent, NoteOffEvent

from .appconfig import load_keyboards

def create_client(suffix):
    return SequencerClient("simple-midi-daw_" + suffix)

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
    # TODO: find the synth port
    synthPort = client.list_ports(output=True)[0]
    for_every_keyboard(lambda port : client.subscribe_port(port, synthPort))

def event_listener():
    client = create_client("listener")
    port = client.create_port("midiIn", WRITE_PORT)
    for_every_keyboard(lambda kbd_port : client.subscribe_port(kbd_port, port))
    while True:
            print("Awaiting event...")
            event = client.event_input()
            print(repr(event))

def metronome():
    client = create_client("metronome")
    port = client.create_port("midiOut")

    # TODO: should match the synth
    list(map(lambda dest_port: port.connect_to(dest_port), client.list_ports(output=True)))

    while True:
        print("Sending note.")
        send_note(client, port)
        time.sleep(1)

def send_note(client, port):
    event1 = NoteOnEvent(note=60, velocity=64, channel=9)
    client.event_output(event1)
    client.drain_output()
    time.sleep(1)
    event2 = NoteOffEvent(note=60, channel=9)
    client.event_output(event2)
    client.drain_output()