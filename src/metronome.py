from alsa_midi import WRITE_PORT, ControlChangeEvent
from .midi import subscribe_keyboards_to_synth, connect_port_to_synth, connect_to_every_keyboard, send_note, create_client, create_output_port, create_input_port, for_every_keyboard
from .appconfig import load_common

class Metronome:
    def __init__(self, inbox):
        self.inbox = inbox
        self.active = True

    def run(self):
        config = load_common()['metronome']
        client = create_client("metronome")
        port = create_output_port(client)
        connect_port_to_synth(client, port)

        self.enabled = config.getboolean("enabled")
        bpm = int(config['bpm'])
        beat_primary_note = config['beat_primary_note']
        beat_primary_velocity = config['beat_primary_velocity']
        beat_secondary_note = config['beat_secondary_note']
        beat_secondary_velocity = config['beat_secondary_velocity']
        beat_time = config['beat_time'].split("/")
        beat_time_beats = int(beat_time[0])
        beat_time_measure = int(beat_time[1])
        channel = config['channel']
        current_beat = 0
        while self.active:
            self.check_inbox()
            if self.enabled:
                print("Tick {}/{}".format(current_beat+1, beat_time_measure))
                wait = 60 / bpm
                try:
                    if current_beat == 0:
                        send_note(client, port, channel, beat_primary_note, beat_primary_velocity, wait)
                    else:
                        send_note(client, port, channel, beat_secondary_note, beat_secondary_velocity, wait)
                except:
                    print("EXCEPTION sending metronome note. Exiting.")
                    raise
            current_beat = (current_beat + 1) % beat_time_measure

    def check_inbox(self):
        while self.inbox:
            msg = self.inbox.popleft()
            self.on_message(msg)
    
    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in metronome: " + repr(msg))
        if (msg == "exit"):
            self.active = False
        else:
            # TODO: other messages?
            self.enabled = not self.enabled
