import subprocess
from threading import Thread
import time
from alsa_midi import SequencerClient, READ_PORT, WRITE_PORT, NoteOnEvent, NoteOffEvent

from .appconfig import load_keyboards

def create_client(suffix):
    # TODO: extract app name
    return SequencerClient("simple-midi-daw_" + suffix)

def create_input_port(client):
    # TODO: name is not unique
    return client.create_port("midiIn", WRITE_PORT)

def create_output_port(client):
    # TODO: name is not unique
    return client.create_port("midiOut", READ_PORT)

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

def connect_port_to_synth(client, port):
    synthPort = find_synth_port(client)
    port.connect_to(synthPort)
    
def connect_keyboard_to_synth():
    keyboardCfg = load_keyboards()
    keyboardClientName = keyboardCfg['description']['client_name']
    keyboardPortName = keyboardCfg['description']['client_port_name']
    print("Expected MIDI keyboard: " + keyboardClientName)
    client = create_client("keyboard")
    synthPort = find_synth_port(client)
    for_every_keyboard(lambda port : client.subscribe_port(port, synthPort))

def connect_to_every_keyboard(client):
    port = create_input_port(client)
    for_every_keyboard(lambda kbd_port : client.subscribe_port(kbd_port, port))

def send_note(client, port, channel, note, velocity, wait):
    event1 = NoteOnEvent(note=note, velocity=velocity, channel=channel)
    client.event_output_buffer(event1)
    client.drain_output()
    time.sleep(wait)
    event2 = NoteOffEvent(note=note, channel=channel)
    client.event_output_buffer(event2)
    client.drain_output()
