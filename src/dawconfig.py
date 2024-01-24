from .appconfig import load_common, load_keyboards

class DawConfig:
    def __init__(self):
        self.cc = load_common()
        # TODO: load during plug in event?
        # TODO: load based on event source (midi port - keyboard)?
        self.kc = load_keyboards()
        # TODO: migrate name
        self.config = self.kc

    def get_section(self, section):
        # TODO: check / default
        return self.config[section]

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

    def get_surface_value(self, surface, key, default=None):
        surface_config = self.get_surface_config(surface)
        if key in surface_config:
            return surface_config['function']
        else:
            return default
