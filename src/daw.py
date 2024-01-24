from .appservice import AppService
from .dawconfig import DawConfig
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
        self.cfg = DawConfig()

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
        cfg = self.cfg
        event = msg.event
        print(f"{msg.source_type}: " + repr(event))
        if event.type == "control_change":            
            if (cfg.is_key_pressed(event, "click")):
                self.metronomeInbox.append("click")
            elif (cfg.is_key_pressed(event, "play")):
                self.playbackInbox.append("play")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 23, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 21, 2))
                self.kbdInbox.append(KbdDisplayTextOp("PLAY"))
            elif (cfg.is_key_pressed(event, "stop")):
                self.playbackInbox.append("stop")
                self.recorderInbox.append("stop")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 10, 0))
                self.kbdInbox.append(KbdDisplayTextOp())
            elif (cfg.is_key_pressed(event, "record")):
                self.recorderInbox.append("record")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 106, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 72, 1))
                self.kbdInbox.append(KbdDisplayTextOp("REC"))
            elif (cfg.is_key_pressed(event, "loop")):
                self.playbackInbox.append("loop")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 23, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 38, 2))
                self.kbdInbox.append(KbdDisplayTextOp("LOOP"))
        if msg.source_type == "midi":
            self.synthInbox.append(msg)
            self.recorderInbox.append(msg)
        if msg.source_type == "daw":
            surface = cfg.get_event_surface(event)
            if surface != None:
                fn = cfg.get_surface_value(surface, "function")
                if fn == 'metronome':
                    if event.type == 'note_on' and event.velocity > 0:
                        self.metronomeInbox.append("tap")

    def on_metronome_tick(self, msg):
        self.playbackInbox.put(msg)
        self.recorderInbox.put(msg)
        self.kbdInbox.put(msg)
