from .midi import create_client, create_output_port, find_keyboard_port, send_note_on, send_note_off, send_sysex
from .appconfig import load_common, load_keyboards
from .appservice import AppService

class KbdOperation:
    def __init__(self, operation):
        self.operation = operation

class KbdColorOp(KbdOperation):
    def __init__(self, surface_type, surface_index, color, color_mode=0):
        super().__init__("color")
        self.surface_type = surface_type
        self.surface_index = surface_index
        self.color = color
        self.color_mode = color_mode

class MidiKeyboard(AppService):
    def __init__(sef, inbox):
        super().__init__(inbox)
    
    def startup(self):
        self.client = create_client("keyboard")
        self.port = create_output_port(self.client)
        self.enter_daw_mode()

    def shutdown(self):
        self.leave_daw_mode()

    def enter_daw_mode(self):
        self.config = load_keyboards()
        daw_enable = self.config['daw.enable']
        kbd_port = find_keyboard_port(port_type='daw')
        self.port.connect_to(kbd_port)
        send_note_on(self.client, daw_enable['chan'], daw_enable['key'], daw_enable['val'])
        # TODO: remove demo
        send_sysex(self.client, b'\xF0\x00\x20\x29\x02\x0F\x04\x00' + bytearray("Simple MIDI DAW", 'utf-8') + b'\xF7')

    def leave_daw_mode(self):
        daw_disable = self.config['daw.disable']
        send_note_on(self.client, 0, 112, 0)
        send_note_on(self.client, daw_disable['chan'], daw_disable['key'], daw_disable['val'])

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in Keyboard: " + repr(msg))
        if (isinstance(msg, KbdOperation)):
            if (isinstance(msg, KbdColorOp)):
                if msg.surface_type == "session":
                    self.send_color_to_session_pad(msg.color, msg.color_mode, msg.surface_index)
                elif msg.surface_type == "drum":
                    self.send_color_to_drum_pad(msg.color, msg.color_mode, msg.surface_index)
                else:
                    print("Unknown surface type " + msg.surface_type)

    def send_color_to_session_pad(self, color, mode, index):
        # TODO: check it exists
        config = self.config['daw.surfaces.session.' + str(index)]
        self.send_color_to_surface(color, mode, config['index'])

    def send_color_to_drum_pad(self, color, mode, index):
        # TODO: check it exists
        config = self.config['daw.surfaces.drum.' + str(index)]
        self.send_color_to_surface(color, mode, config['index'])

    def send_color_to_surface(self, color, mode, surface):
        send_note_on(self.client, mode, surface, color)
