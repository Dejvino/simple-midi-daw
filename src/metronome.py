import time
from alsa_midi import WRITE_PORT, ControlChangeEvent
from .midi import connect_port_to_synth, send_note, create_client, create_output_port
from .appconfig import load_common
from .appservice import AppService

class Metronome(AppService):
    def __init__(self, inbox):
        super().__init__(inbox)

    def startup(self):
        self.config = config = load_common()['metronome']
        self.client = client = create_client("metronome")
        self.port = port = create_output_port(client)
        connect_port_to_synth(client, port)
        self.enabled = config.getboolean('enabled')
        self.current_beat = 0
        
    def tick(self):
        config = self.config
        client = self.client
        port = self.port
        bpm = int(config['bpm'])
        beat_primary_note = config['beat_primary_note']
        beat_primary_velocity = config['beat_primary_velocity']
        beat_secondary_note = config['beat_secondary_note']
        beat_secondary_velocity = config['beat_secondary_velocity']
        beat_time = config['beat_time'].split("/")
        beat_time_beats = int(beat_time[0])
        beat_time_measure = int(beat_time[1])
        channel = config['channel']

        if self.enabled:
            #print("Tick {}/{}".format(current_beat+1, beat_time_measure))
            wait = 60 / bpm
            try:
                if self.current_beat == 0:
                    send_note(client, channel, beat_primary_note, beat_primary_velocity, wait)
                else:
                    send_note(client, channel, beat_secondary_note, beat_secondary_velocity, wait)
            except:
                print("EXCEPTION sending metronome note. Exiting.")
                raise
        else:
            time.sleep(wait)
        self.current_beat = (self.current_beat + 1) % beat_time_measure

    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in metronome: " + repr(msg))
        # TODO: other messages?
        self.enabled = not self.enabled
