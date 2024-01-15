import time
import mido

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
