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
        # TODO: load based on event source (midi port - keyboard)?
        # TODO: load during plug in event?
        self.config = load_keyboards()

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
        print(f"{msg.source_type}: " + repr(event))
        if event.type == "control_change":            
            if (self.is_key_pressed(event, "click")):
                self.metronomeInbox.append("click")
            elif (self.is_key_pressed(event, "play")):
                self.playbackInbox.append("play")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 23, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 21, 2))
                self.kbdInbox.append(KbdDisplayTextOp("PLAY"))
            elif (self.is_key_pressed(event, "stop")):
                self.playbackInbox.append("stop")
                self.recorderInbox.append("stop")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 10, 0))
                self.kbdInbox.append(KbdDisplayTextOp())
            elif (self.is_key_pressed(event, "record")):
                self.recorderInbox.append("record")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 106, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 72, 1))
                self.kbdInbox.append(KbdDisplayTextOp("REC"))
            elif (self.is_key_pressed(event, "loop")):
                self.playbackInbox.append("loop")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", 0, 23, 0))
                self.kbdInbox.append(KbdColorOp("session", 0, 38, 2))
                self.kbdInbox.append(KbdDisplayTextOp("LOOP"))
        if msg.source_type == "midi":
            self.synthInbox.append(msg)
            self.recorderInbox.append(msg)
        if msg.source_type == "daw":
            surface = self.get_event_surface(event)
            if surface != None:
                surface_config = self.get_surface_config(surface)
                if 'function' in surface_config:
                    fn = surface_config['function']
                    if fn == 'metronome':
                        if event.type == 'note_on' and event.velocity > 0:
                            self.metronomeInbox.append("tap")

    def on_metronome_tick(self, msg):
        self.playbackInbox.put(msg)
        self.recorderInbox.put(msg)
        self.kbdInbox.put(msg)

    # TODO: move to keyboard class?
    def is_event_matching_config(self, event, config_key):
        config = self.config
        try:
            mapping = config[config_key]
            if str(event.channel) != mapping['chan']:
                return False
            if hasattr(event, "control") and str(event.control) != mapping['key']:
                return False
            if hasattr(event, "note") and str(event.note) != mapping['index']:
                return False
            return True
        except KeyError as e:
            print("ConfigKeyError for key " + config_key + ": " + str(e))
            return False

    def is_key(self, event, keyname):
        return self.is_event_matching_config(event, 'mapping.' + keyname)

    def is_key_pressed(self, event, keyname):
        return self.is_key(event, keyname) and event.value > 60

    def is_surface(self, event, surface):
        return self.is_event_matching_config(event, 'daw.surfaces.' + surface)

    def get_event_surface(self, event):
        cfg = self.config
        # TODO: drums?
        width = int(cfg['daw.surfaces.session']['width'])
        rows = int(cfg['daw.surfaces.session']['rows'])
        for prefix in ["session"]:
            for index in range(0, width*rows):
                surface = prefix + '.' + str(index)
                if self.is_surface(event, surface):
                    return surface
        return None

    def get_surface_config(self, surface):
        return self.config['daw.surfaces.' + surface]