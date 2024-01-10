from .midi import create_client, create_input_port, for_every_keyboard
from .appconfig import load_common, load_keyboards

class MidiEvent:
    def __init__(self, source_type, event):
        self.source_type = source_type
        self.event = event
        
class EventListener:
    def __init__(self, dawInbox):
        self.dawInbox = dawInbox

    def run(self):    
        client = create_client("listener")
        port = create_input_port(client)
        self.port_type_map = {}
        for port_type in ["midi", "daw"]:
            def register_keyboard(kbd_port):
                client.subscribe_port(kbd_port, port)
                self.port_type_map[address_str(kbd_port)] = port_type
            for_every_keyboard(register_keyboard, port_type)
        while True:
            event = client.event_input()
            self.on_event(event)
    
    def on_event(self, event):
        #print("Event in listener: " + repr(event) + " from " + repr(event.source))
        # TODO: load based on event source (midi port - keyboard)
        config = load_keyboards()
        # TODO: check it is available
        source_type = self.port_type_map[address_str(event.source)]
        self.dawInbox.append(MidiEvent(source_type, event))
            
def address_str(port):
    # TODO: other input types?
    return f"{port.client_id}:{port.port_id}"
