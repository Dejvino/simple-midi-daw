import os
import time
from alsa_midi import SequencerClient, READ_PORT, NoteOnEvent, NoteOffEvent

synth = None

def spawn_synth():
    print("Spawning synthesizer")
    synth = os.popen("fluidsynth -s")
    print("OK")

def main():
    spawn_synth()

    print("Creating MIDI client")
    client = SequencerClient("my client")
    print("Creating port")
    port = client.create_port("output", caps=READ_PORT)
    print("Connecting to destination port")
    dest_port = client.list_ports(output=True)[0]
    port.connect_to(dest_port)
    print("Sending note")
    event1 = NoteOnEvent(note=60, velocity=64, channel=0)
    client.event_output(event1)
    client.drain_output()
    print("Waiting")
    time.sleep(1)
    print("Ending note")
    event2 = NoteOffEvent(note=60, channel=0)
    client.event_output(event2)
    client.drain_output()
    print("Done!")

