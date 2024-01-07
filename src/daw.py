from .midi import create_client, create_output_port, find_keyboard_port, send_note_on, send_note_off, send_sysex
from .appconfig import load_common, load_keyboards
from .appservice import AppService

class Daw(AppService):
    def __init__(self, dawInbox):
        super().__init__(dawInbox)

    def startup(self):
        self.client = create_client("daw")
        self.port = create_output_port(self.client)
        self.enter_daw_mode()

    def shutdown(self):
        self.leave_daw_mode()

    def enter_daw_mode(self):
        config = load_keyboards()
        daw_enable = config['daw.enable']
        kbd_port = find_keyboard_port(port_type='daw')
        self.port.connect_to(kbd_port)
        send_note_on(self.client, daw_enable['chan'], daw_enable['key'], daw_enable['val'])
        # TODO: remove demo
        send_note_on(self.client, 0, 112, 5)
        send_note_on(self.client, 1, 96, 19)
        send_note_on(self.client, 2, 99, 8)
        send_sysex(self.client, b'\xF0\x00\x20\x29\x02\x0F\x04\x00' + bytearray("Simple MIDI DAW", 'utf-8') + b'\xF7')

    def leave_daw_mode(self):
        config = load_keyboards()
        daw_disable = config['daw.disable']
        send_note_on(self.client, 0, 112, 0)
        send_note_on(self.client, daw_disable['chan'], daw_disable['key'], daw_disable['val'])

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in DAW: " + repr(msg))
            
