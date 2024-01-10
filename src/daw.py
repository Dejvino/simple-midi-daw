from alsa_midi import ControlChangeEvent
from .midi import create_client, create_output_port, find_keyboard_port, send_note_on, send_note_off, send_sysex
from .appconfig import load_common, load_keyboards
from .appservice import AppService
from .eventlistener import MidiEvent

class Daw(AppService):
    def __init__(self, dawInbox, kbdInbox, metronomeInbox, playbackInbox):
        super().__init__(dawInbox)
        self.kbdInbox = kbdInbox
        self.metronomeInbox = metronomeInbox
        self.playbackInbox = playbackInbox

    def startup(self):
        pass

    def shutdown(self):
        pass

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in DAW: " + repr(msg))
        if (isinstance(msg, MidiEvent)):
            self.on_midi_event(msg)

    def on_midi_event(self, msg):
        event = msg.event
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
    