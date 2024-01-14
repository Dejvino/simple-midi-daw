from .appconfig import load_common, load_keyboards
from .midi import MidiEvent, MidiClient, for_every_keyboard

class EventListener:
    def __init__(self, dawInbox):
        self.dawInbox = dawInbox

    def run(self):    
        client = MidiClient("listener")
        port = client.create_input_port()
        self.port_type_map = {}
        for port_type in ["midi", "daw"]:
            def register_keyboard(kbd_port):
                client.connect_to_output_port(kbd_port)
                self.port_type_map[kbd_port] = port_type
            for_every_keyboard(register_keyboard, port_type)
        while True:
            for source_port, event in client.read_events():
                self.on_event(event, source_port)
    
    def on_event(self, event, source_port):
        # TODO: load based on event source (midi port - keyboard)
        config = load_keyboards()
        source_type = self.port_type_map.get(source_port.name, "midi")
        self.dawInbox.append(MidiEvent(source_type, event))
