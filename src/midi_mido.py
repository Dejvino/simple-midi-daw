import subprocess
from threading import Thread
import time
import mido

from .appconfig import load_keyboards

class MidiClient:
    def __init__(self, suffix):
        self.suffix = suffix
        self.ports = []

    def add_port(self, port):
        self.ports.append(port)


def create_client(suffix):
    return MidiClient(suffix)

def create_input_port(client):
    port = mido.open_input("midiIn", virtual=True)
    client.add_port(port)
    return port

def create_output_port(client):
    port = mido.open_output("midiOut")
    client.add_port(port)
    return port

def create_inout_port(client):
    port = mido.open_ioport("midiInOut")
    client.add_port(port)
    return port

def send_panic_event(client, target_port):
    target_port.panic()

def send_panic_event_to_synth():
    client = create_client("panic")
    send_panic_event(client, find_synth_port(client))

def find_synth_port(client):
    # TODO: find the synth based on name
    return mido.get_input_names()[0]

def find_every_keyboard_port(port_type='midi'):
    keyboardCfg = load_keyboards()
    keyboardClientName = keyboardCfg['description']['client_name']
    keyboardPortName = keyboardCfg['description']['client_port_' + port_type + '_name']
    client = create_client("keyboard")
    inPorts = mido.get_input_names()
    for port in inPorts:
        if port.find(keyboardClientName) != -1 and port.find(keyboardPortName) != -1:
            yield port

def find_keyboard_port(port_type='midi'):
    keyboards = list(find_every_keyboard_port(port_type))
    assert len(keyboards) > 0
    return keyboards[0]

def for_every_keyboard(fn, port_type='midi'):
    for port in find_every_keyboard_port(port_type):
        fn(port)

def send_note_on(port, channel, note, velocity):
    event = mido.Message('note_on', note=note, channel=channel, velocity=velocity)
    port.send(event)

def send_note_off(port, channel, note):
    event = mido.Message('note_off', note=note, channel=channel)
    port.send(event)

def send_note(client, channel, note, velocity, wait):
    send_note_on(client, channel, note, velocity)
    time.sleep(wait)
    send_note_off(client, channel, note)

def send_sysex(client, data):
    pass

def read_events(client):
    events = mido.ports.multi_receive(client.ports, yield_ports=True)
    return events

def connect_to_output_port(client, port):
    port = mido.open_input(port)
    client.add_port(port)
