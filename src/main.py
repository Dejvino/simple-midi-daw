import subprocess
import time
from alsa_midi import SequencerClient, READ_PORT, NoteOnEvent, NoteOffEvent

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth

def send_note():
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

def main():
    with spawn_synth() as synth:
        send_note()
        synth.terminate()

