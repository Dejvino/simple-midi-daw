from .midikeyboard import KbdColorOp, KbdDisplayTextOp

class DawSurfaces():
    def __init__(self, kbdInbox):
        self.kbdInbox = kbdInbox
        self._active = 0
        self.cfg = None
        # TODO: load from config
        cbn = {}
        cbn['default'] = 1
        cbn['active'] = 20
        cbn['play_scheduled'] = 19
        cbn['play'] = 21
        cbn['paused'] = 22
        cbn['record_scheduled'] = 107
        cbn['record_active'] = 72
        cbn['loop'] = 36
        cbn['loop_scheduled'] = 37
        cbn['loop_paused'] = 38
        self.colors_by_name = cbn

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self.set_color(self._active, "default")
        self._active = value
        self.set_color(self._active, "active")
    
    def init(self, cfg):
        self.cfg = cfg
        for surface in self.cfg.get_all_surfaces():
            self.set_color(surface, "default")
        self.set_color_on_active("active")

    def set_color(self, surface, main, flash=None, pulse=None):
        if main != None:
            self.kbdInbox.append(KbdColorOp("session", surface, self.get_color_by_name(main), 0))
        if flash != None:
            self.kbdInbox.append(KbdColorOp("session", surface, self.get_color_by_name(flash), 1))
        if pulse != None:
            self.kbdInbox.append(KbdColorOp("session", surface, self.get_color_by_name(pulse), 2))

    def set_color_on_active(self, main, flash=None, pulse=None):
        self.set_color(self.active, main, flash=flash, pulse=pulse)
        
    def get_color_by_name(self, name):
        if name in self.colors_by_name:
            return self.colors_by_name[name]
        raise Exception(f"Unknown color '{name}'")
