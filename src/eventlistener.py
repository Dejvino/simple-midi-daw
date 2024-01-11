from . import midi_mido as midi
from .appconfig import load_common, load_keyboards

class MidiEvent:
    def __init__(self, source_type, event):
        self.source_type = source_type
        self.event = event
        
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
        #print("Event in listener: " + repr(event) + " from " + repr(event.source))
        # TODO: load based on event source (midi port - keyboard)
        config = load_keyboards()
        # TODO: check it is available
        source_type = self.port_type_map[source_port.name]
        self.dawInbox.append(MidiEvent(source_type, event))
            
def address_str(port):
    # TODO: other input types?
    return f"{port.client_id}:{port.port_id}"
