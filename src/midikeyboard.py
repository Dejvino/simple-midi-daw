from .midi import MidiClient, find_keyboard_port
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

class KbdDisplayTextOp(KbdOperation):
    def __init__(self, message=None):
        super().__init__("display-text")
        self.message = message

class MidiKeyboard(AppService):
    def __init__(sef, inbox):
        super().__init__(inbox)
    
    def startup(self):
        self.config = load_keyboards()
        self.client = MidiClient("keyboard")
        kbd_port = find_keyboard_port(port_type='daw')
        self.port = self.client.create_output_port(kbd_port)
        self.enter_daw_mode()

    def shutdown(self):
        self.leave_daw_mode()

    def enter_daw_mode(self):
        cfg = self.config['daw.enable']
        self.client.send_note_on(int(cfg['chan']), int(cfg['key']), int(cfg['val']))

    def leave_daw_mode(self):
        self.client.send_note_on(0, 112, 0)
        cfg = self.config['daw.disable']
        self.client.send_note_on(int(cfg['chan']), int(cfg['key']), int(cfg['val']))

    def on_message(self, msg):
        # TODO: switch msg type
        #print("Message in Keyboard: " + repr(msg))
        if (isinstance(msg, KbdOperation)):
            if (isinstance(msg, KbdColorOp)):
                if msg.surface_type == "session":
                    self.send_color_to_session_pad(msg.color, msg.color_mode, msg.surface_index)
                elif msg.surface_type == "drum":
                    self.send_color_to_drum_pad(msg.color, msg.color_mode, msg.surface_index)
                else:
                    print("Unknown surface type " + msg.surface_type)
            elif (isinstance(msg, KbdDisplayTextOp)):
                self.send_display_text(msg.message)

    def send_color_to_session_pad(self, color, mode, index):
        # TODO: check it exists
        config = self.config['daw.surfaces.session.' + str(index)]
        self.send_color_to_surface(color, mode, int(config['index']))

    def send_color_to_drum_pad(self, color, mode, index):
        # TODO: check it exists
        config = self.config['daw.surfaces.drum.' + str(index)]
        self.send_color_to_surface(color, mode, int(config['index']))

    def send_color_to_surface(self, color, mode, surface):
        self.client.send_note_on(mode, surface, color)

    def _send_display_text_row(self, msg, row):
        # TODO: check it exists
        config_display = self.config['daw.display']
        display_width = int(config_display['width'])
        display_rows = int(config_display['rows'])
        
        if row >= display_rows:
            return
        row_msg, rest_msg = extract_row(msg, display_width)
        params = {
            'row': row,
            'message': row_msg
        }
        # TODO: check it exists
        sysex = build_sysex_message(self.config['daw.display.set'], params)
        self.client.send_sysex(sysex)

    def _send_display_text_clear(self):
        params = {}
        # TODO: check it exists
        sysex = build_sysex_message(self.config['daw.display.clear'], params)
        self.client.send_sysex(sysex)

    def send_display_text(self, msg):
        if msg == None:
            self._send_display_text_clear()
        else:
            self._send_display_text_row(msg, 0)
    
def extract_row(msg, row_width):
    end = row_width
    rest = row_width
    newline_pos = msg.find("\n")
    if newline_pos != -1 and newline_pos < end:
        end = newline_pos
        rest = newline_pos + 1
    return (msg[0:end], msg[rest:])

def build_sysex_message(config, params):
    result = []
    sysex_i = 0
    while 'sysex_' + str(sysex_i) in config:
        sysex_key = 'sysex_' + str(sysex_i)
        sysex_template = config[sysex_key]
        template_op, *template_data = sysex_template.split(":")
        if template_op == 'hex' or template_op == 'dec':
            if template_op == 'hex':
                base = 16
            else:
                base = 10
            sysex = bytes(map(lambda x : int(x, base), template_data[0].split(" ")))
        elif template_op in params:
            param = params[template_op]
            if isinstance(param, str):
                sysex = bytes(param, 'utf-8')
            elif isinstance(param, int):
                sysex = bytes([param])
            else:
                sysex = bytes(param)
        else:
            raise f"Unsupported template operation '{template_op}' in '{sysex_key} = {repr(template_data)}'"
        result.append(sysex)
        sysex_i = sysex_i + 1
    return b''.join(result)