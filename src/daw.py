from .appconfig import load_common, load_keyboards
from .appservice import AppService
from .midi import MidiEvent
from .midikeyboard import KbdColorOp, KbdDisplayTextOp
from .metronome import MetronomeTick

class Daw(AppService):
    def __init__(self, dawInbox, kbdInbox, synthInbox, metronomeInbox, playbackInbox, recorderInbox):
        super().__init__(dawInbox)
        self.kbdInbox = kbdInbox
        self.synthInbox = synthInbox
        self.metronomeInbox = metronomeInbox
        self.playbackInbox = playbackInbox
        self.recorderInbox = recorderInbox

    def startup(self):
        pass

    def shutdown(self):
        pass

    def on_message(self, msg):
        if (isinstance(msg, MidiEvent)):
            self.on_midi_event(msg)
        elif isinstance(msg, MetronomeTick):
            self.on_metronome_tick(msg)
        else:
            print("Message in DAW not processed: " + repr(msg))

    def on_midi_event(self, msg):
        event = msg.event
        #print(f"{msg.source_type}: " + repr(event))
        # TODO: load based on event source (midi port - keyboard)
        config = load_keyboards()
        if event.type == "control_change":
            def is_key(config, event, keyname):
                # TODO: check mapping exists
                mapping = config['mapping.' + keyname]
                return str(event.channel) == mapping['chan'] and str(event.control) == mapping['key']
            def is_key_pressed(config, event, keyname):
                return is_key(config, event, keyname) and event.value > 60
            if (is_key_pressed(config, event, "click")):
                self.metronomeInbox.append("click")
            elif (is_key_pressed(config, event, "play")):
                self.playbackInbox.append("play")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 23, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 21, 2))
                self.kbdInbox.append(KbdDisplayTextOp("PLAY"))
            elif (is_key_pressed(config, event, "stop")):
                self.playbackInbox.append("stop")
                self.recorderInbox.append("stop")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 10, 0))
                self.kbdInbox.append(KbdDisplayTextOp())
            elif (is_key_pressed(config, event, "record")):
                self.recorderInbox.append("record")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 106, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 72, 1))
                self.kbdInbox.append(KbdDisplayTextOp("REC"))
            elif (is_key_pressed(config, event, "loop")):
                self.playbackInbox.append("loop")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 23, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 38, 2))
                self.kbdInbox.append(KbdDisplayTextOp("LOOP"))
        if msg.source_type == "midi":
            self.synthInbox.append(msg)
            self.recorderInbox.append(msg)

    def on_metronome_tick(self, msg):
        self.playbackInbox.put(msg)
        self.recorderInbox.put(msg)
        self.kbdInbox.put(msg)
