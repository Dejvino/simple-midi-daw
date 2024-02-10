from .appservice import AppService
from .dawconfig import DawConfig
from .midi import MidiEvent
from .metronome import MetronomeTick
from .playback import PlaybackMsg
from .dawsurfaces import DawSurfaces
from .midikeyboard import KbdColorOp, KbdDisplayTextOp

class Daw(AppService):
    def __init__(self, dawInbox, kbdInbox, synthInbox, metronomeInbox, playbackInbox, recorderInbox):
        super().__init__(dawInbox)
        self.kbdInbox = kbdInbox
        self.synthInbox = synthInbox
        self.metronomeInbox = metronomeInbox
        self.playbackInbox = playbackInbox
        self.recorderInbox = recorderInbox
        self.surfaces = DawSurfaces(kbdInbox)

    def startup(self):
        self.cfg = DawConfig()
        self.surfaces.init(self.cfg)

    def shutdown(self):
        pass

    def on_message(self, msg):
        if (isinstance(msg, MidiEvent)):
            self.on_midi_event(msg)
        elif isinstance(msg, MetronomeTick):
            self.on_metronome_tick(msg)
        elif isinstance(msg, PlaybackMsg):
            self.on_playback(msg)
        else:
            print("Message in DAW not processed: " + repr(msg))

    def on_midi_event(self, msg):
        cfg = self.cfg
        event = msg.event
        if event.type == "control_change":            
            if (cfg.is_key_pressed(event, "click")):
                self.on_press_click()
            elif (cfg.is_key_pressed(event, "play")):
                self.on_press_play()
            elif (cfg.is_key_pressed(event, "stop")):
                self.on_press_stop()
            elif (cfg.is_key_pressed(event, "record")):
                self.on_press_record()
            elif (cfg.is_key_pressed(event, "loop")):
                self.on_press_loop()
        if msg.source_type == "midi":
            self.on_midi_sound(msg)
        if msg.source_type == "daw":
            surface = cfg.get_event_surface(event)
            if surface != None:
                fn = cfg.get_surface_value(surface, "function")
                if fn == 'metronome':
                    if event.type == 'note_on' and event.velocity > 0:
                        self.metronomeInbox.append("tap")
                if fn == 'session':
                    self.surfaces.active = surface

    def on_midi_sound(self, msg):
        msg.event.channel = int(self.surfaces.active)
        self.synthInbox.append(msg)
        self.recorderInbox.append(msg)

    def on_press_click(self):
        self.metronomeInbox.append("click")
        
    def on_press_play(self):
        self.playbackInbox.append(PlaybackMsg("play", channel=self.get_active_channel()))
        self.surfaces.set_color_on_active("play_scheduled")

    def on_press_stop(self):
        self.playbackInbox.append(PlaybackMsg("stop", channel=self.get_active_channel()))
        self.recorderInbox.append("stop")
        self.surfaces.set_color_on_active("active")

    def on_press_record(self):
        self.recorderInbox.append("record")
        self.surfaces.set_color_on_active("record_scheduled")

    def on_press_loop(self):
        self.playbackInbox.append(PlaybackMsg("loop", channel=self.get_active_channel()))
        self.surfaces.set_color_on_active("loop_scheduled")

    def on_metronome_tick(self, msg):
        self.playbackInbox.put(msg)
        self.recorderInbox.put(msg)
        self.kbdInbox.put(msg)

    def on_playback(self, msg):
        op = msg.operation
        ch = self.map_channel_to_surface(msg.channel)
        if op in ["play_stopped", "loop_stopped"]:
            self.surfaces.set_color(ch, "default")
        elif op == "play_paused":
            self.surfaces.set_color(ch, "paused")
        elif op == "play_started":
            self.surfaces.set_color(ch, "play")
        elif op == "loop_paused":
            self.surfaces.set_color(ch, "loop_paused")
        elif op == "loop_started":
            self.surfaces.set_color(ch, "loop")
        else:
            print("Unknown playback msg op: ", op)

    def map_channel_to_surface(self, channel):
        for surface in self.cfg.get_surfaces_matching("session_offset", channel):
            return surface
        return None

    def map_surface_to_channel(self, surface):
        return self.cfg.get_surface_value(surface, "session_offset")

    def get_active_channel(self):
        return self.map_surface_to_channel(self.surfaces.active)