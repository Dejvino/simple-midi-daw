import subprocess
from threading import Thread
import time
from alsa_midi import SequencerClient, READ_PORT, WRITE_PORT, NoteOnEvent, NoteOffEvent, ResetEvent

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

def send_panic_event(client, target_port):
    port = create_output_port(client)
    port.connect_to(target_port)
    event1 = ResetEvent() # TODO: this works, but it resets the instruments
    client.event_output_buffer(event1)
    client.drain_output()

def send_panic_event_to_synth():
    client = create_client("panic")
    send_panic_event(client, find_synth_port(client))

def find_synth_port(client):
    # TODO: find the synth based on name
    return client.list_ports(output=True)[0]

def find_every_keyboard_port():
    keyboardCfg = load_keyboards()
    keyboardClientName = keyboardCfg['description']['client_name']
    keyboardPortName = keyboardCfg['description']['client_port_name']
    client = create_client("keyboard")
    inPorts = client.list_ports(input=True)
    for port in inPorts:
        if port.client_name == keyboardClientName and port.name == keyboardPortName:
            yield port

def find_keyboard_port():
    return list(find_every_keyboard_port())[0]

def for_every_keyboard(fn):
    for port in find_every_keyboard_port():
        fn(port)

def connect_port_to_synth(client, port):
    synth_port = find_synth_port(client)
    port.connect_to(synth_port)

def subscribe_keyboards_to_synth():
    client = create_client("keyboard-subscriber")
    synth_port = find_synth_port(client)
    for_every_keyboard(lambda kbd_port : client.subscribe_port(kbd_port, synth_port))

def connect_to_every_keyboard(client):
    port = create_input_port(client)
    def connect_port(kbd_port):
        client.subscribe_port(kbd_port, port)
        #port.connect_to(kbd_port)
    for_every_keyboard(connect_port)

def send_note(client, port, channel, note, velocity, wait):
    event1 = NoteOnEvent(note=note, velocity=velocity, channel=channel)
    client.event_output_buffer(event1)
    client.drain_output()
    time.sleep(wait)
    event2 = NoteOffEvent(note=note, channel=channel)
    client.event_output_buffer(event2)
    client.drain_output()
