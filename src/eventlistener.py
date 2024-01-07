from alsa_midi import WRITE_PORT, ControlChangeEvent
from .midi import subscribe_keyboards_to_synth, connect_port_to_synth, connect_to_every_keyboard, send_note, create_client, create_output_port, create_input_port, for_every_keyboard
from .appconfig import load_common, load_keyboards

class EventListener:
    def __init__(self, dawInbox, metronomeInbox, playbackInbox):
        self.dawInbox = dawInbox
        self.metronomeInbox = metronomeInbox
        self.playbackInbox = playbackInbox

    def run(self):    
        client = create_client("listener")
        # TODO: move to midi.py
        port = client.create_port("midiIn", WRITE_PORT)
        for port_type in ["midi", "daw"]:
            for_every_keyboard(lambda kbd_port : client.subscribe_port(kbd_port, port), port_type)
        while True:
            event = client.event_input()
            self.on_event(event)
    
    def on_event(self, event):
        print("Event in listener: " + repr(event))
        config = load_keyboards()
        # TODO: load based on event source (midi port - keyboard)
        if (isinstance(event, ControlChangeEvent)):
            def is_key(config, event, keyname):
                # TODO: check mapping exists
                mapping = config['mapping.' + keyname]
                return str(event.channel) == mapping['chan'] and str(event.param) == mapping['key']
            def is_key_pressed(config, event, keyname):
                return is_key(config, event, keyname) and event.value > 60
            if (is_key_pressed(config, event, "click")):
                self.metronomeInbox.append("click")
            elif (is_key_pressed(config, event, "play")):
                self.playbackInbox.append("play")
            elif (is_key_pressed(config, event, "stop")):
                self.playbackInbox.append("stop")
            elif (is_key_pressed(config, event, "record")):
                self.playbackInbox.append("record")
            elif (is_key_pressed(config, event, "loop")):
                self.playbackInbox.append("loop")
            
