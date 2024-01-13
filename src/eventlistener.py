from . import midi_mido as midi
from .appconfig import load_common, load_keyboards
from .midi import MidiEvent

class EventListener:
    def __init__(self, dawInbox):
        self.dawInbox = dawInbox

    def run(self):    
        client = midi.create_client("listener")
        port = midi.create_input_port(client)
        self.port_type_map = {}
        for port_type in ["midi", "daw"]:
            def register_keyboard(kbd_port):
                midi.connect_to_output_port(client, kbd_port)
                self.port_type_map[kbd_port] = port_type
            midi.for_every_keyboard(register_keyboard, port_type)
        while True:
            for source_port, event in midi.read_events(client):
                self.on_event(event, source_port)
    
    def on_event(self, event, source_port):
        # TODO: load based on event source (midi port - keyboard)
        config = load_keyboards()
        source_type = self.port_type_map.get(source_port.name, "midi")
        self.dawInbox.append(MidiEvent(source_type, event))
