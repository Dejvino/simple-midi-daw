import subprocess
from threading import Thread
import time
import mido

from .appconfig import load_keyboards

class MidiEvent:
    def __init__(self, source_type, event):
        self.source_type = source_type
        self.event = event

class MidiClient:
    def __init__(self, suffix):
        self.suffix = suffix
        self.ports = []

    def add_port(self, port):
        self.ports.append(port)

    def send_note_on(self, channel, note, velocity):
        event = mido.Message('note_on', note=note, channel=channel, velocity=velocity)
        # TODO: all ports?
        port = self.ports[0]
        port.send(event)

    def send_note_off(self, channel, note):
        event = mido.Message('note_off', note=note, channel=channel)
        # TODO: all ports?
        port = self.ports[0]
        port.send(event)

    def send_note(self, channel, note, velocity, wait):
        self.send_note_on(channel, note, velocity)
        time.sleep(wait)
        self.send_note_off(channel, note)

    def send_sysex(self, data):
        pass

    def read_events(self):
        events = mido.ports.multi_receive(self.ports, yield_ports=True)
        return events

    def connect_to_output_port(self, port):
        port = mido.open_input(port)
        self.add_port(port)

    def create_input_port(self):
        port = mido.open_input("midiIn", virtual=True)
        self.add_port(port)
        return port

    def create_output_port(self, port_name):
        port = mido.open_output(port_name)
        self.add_port(port)
        return port

    def create_inout_port(self):
        port = mido.open_ioport("midiInOut")
        self.add_port(port)
        return port

def find_every_keyboard_port(port_type='midi'):
    keyboardCfg = load_keyboards()
    keyboardClientName = keyboardCfg['description']['client_name']
    keyboardPortName = keyboardCfg['description']['client_port_' + port_type + '_name']
    client = MidiClient("keyboard")
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
