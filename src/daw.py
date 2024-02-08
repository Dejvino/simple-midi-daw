from .appservice import AppService
from .dawconfig import DawConfig
from .midi import MidiEvent
from .midikeyboard import KbdColorOp, KbdDisplayTextOp
from .metronome import MetronomeTick
from .playback import PlaybackMsg

class Daw(AppService):
    def __init__(self, dawInbox, kbdInbox, synthInbox, metronomeInbox, playbackInbox, recorderInbox):
        super().__init__(dawInbox)
        self.kbdInbox = kbdInbox
        self.synthInbox = synthInbox
        self.metronomeInbox = metronomeInbox
        self.playbackInbox = playbackInbox
        self.recorderInbox = recorderInbox
        self.status_active_session = 0

    def startup(self):
        self.cfg = DawConfig()
        self.color_session_default = 23
        self.color_session_active = 20
        self.color_session_play = 21
        self.color_session_record_scheduled = 107
        self.color_session_record_active = 72
        self.color_session_loop = 36
        for surface in self.cfg.get_all_surfaces():
            self.kbdInbox.append(KbdColorOp("session", surface, self.color_session_default, 0))
        self.kbdInbox.append(KbdColorOp("session", self.status_active_session, self.color_session_active, 0))

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
                self.playbackInbox.append(PlaybackMsg("play", channel=self.status_active_session))
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", self.status_active_session, self.color_session_active, 0))
                self.kbdInbox.append(KbdColorOp("session", self.status_active_session, self.color_session_play, 2))
                self.kbdInbox.append(KbdDisplayTextOp("PLAY"))
            elif (cfg.is_key_pressed(event, "stop")):
                self.playbackInbox.append(PlaybackMsg("stop", channel=self.status_active_session))
                self.recorderInbox.append("stop")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", self.status_active_session, self.color_session_active, 0))
                self.kbdInbox.append(KbdDisplayTextOp())
            elif (cfg.is_key_pressed(event, "record")):
                self.recorderInbox.append("record")
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", self.status_active_session, self.color_session_record_scheduled, 0))
                self.kbdInbox.append(KbdColorOp("session", self.status_active_session, 72, 1))
                self.kbdInbox.append(KbdDisplayTextOp("REC"))
            elif (cfg.is_key_pressed(event, "loop")):
                self.playbackInbox.append(PlaybackMsg("loop", channel=self.status_active_session))
                # TODO: remove demo
                self.kbdInbox.append(KbdColorOp("session", self.status_active_session, self.color_session_loop, 0))
                self.kbdInbox.append(KbdColorOp("session", self.status_active_session, 38, 2))
                self.kbdInbox.append(KbdDisplayTextOp("LOOP"))
        if msg.source_type == "midi":
            msg.event.channel = int(self.status_active_session)
            self.synthInbox.append(msg)
            self.recorderInbox.append(msg)
        if msg.source_type == "daw":
            surface = cfg.get_event_surface(event)
            if surface != None:
                fn = cfg.get_surface_value(surface, "function")
                if fn == 'metronome':
                    if event.type == 'note_on' and event.velocity > 0:
                        self.metronomeInbox.append("tap")
                if fn == 'session':
                    old_session = self.status_active_session
                    new_session = cfg.get_surface_value(surface, "session_offset")
                    if old_session != new_session:
                        self.status_active_session = new_session
                        # TODO: remove demo
                        self.kbdInbox.append(KbdColorOp("session", self.map_session_to_surface(old_session), self.color_session_default, 0))
                        self.kbdInbox.append(KbdColorOp("session", self.map_session_to_surface(new_session), self.color_session_active, 0))

    def map_session_to_surface(self, session):
        for surface in self.cfg.get_surfaces_matching("session_offset", session):
            return surface
        return None

    def on_metronome_tick(self, msg):
        self.playbackInbox.put(msg)
        self.recorderInbox.put(msg)
        self.kbdInbox.put(msg)
