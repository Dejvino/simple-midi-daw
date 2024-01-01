import subprocess
from threading import Thread
import time
from alsa_midi import SequencerClient, READ_PORT, WRITE_PORT, NoteOnEvent, NoteOffEvent

from .appconfig import load_keyboards

def spawn_synth():
    print("Spawning synthesizer")
    synth = subprocess.Popen(["fluidsynth",  "default.sf2", "-s", "-a", "pulseaudio"])
    print("OK")
    time.sleep(1)
    return synth

def create_client(suffix):
    return SequencerClient("simple-midi-daw_" + suffix)

def connect_keyboard_to_synth():
    keyboardCfg = load_keyboards()
    print("Keyboard config: " + repr(keyboardCfg))
    keyboardClientName = keyboardCfg['description']['client_name']
    client = create_client("keyboard")
    # TODO: find the synth port
    synthPort = client.list_ports(output=True)[0]
    print("Synth port: " + repr(synthPort.get_info()))
    # TODO: find the keyboard
    print("Connecting known keyboards to the synth...")
    inPorts = client.list_ports(input=True)
    for port in inPorts:
        portInfo = port.get_info()
        if portInfo.name == keyboardClientName:
            print("Recognized keyboard: " + repr(portInfo))
            client.subscribe_port(port, synthPort)
    print("Done connecting keyboards to the synth.")

def event_listener():
    client = create_client("listener")
    port = client.create_port("midiIn", WRITE_PORT)
    while True:
            print("Awaiting event...")
            event = client.event_input()
            print(repr(event))

def metronome():
    client = create_client("metronome")
    port = client.create_port("midiOut")

    # TODO: should match the synth
    list(map(lambda dest_port: port.connect_to(dest_port), client.list_ports(output=True)))

    while True:
        print("Sending note.")
        send_note(client, port)
        time.sleep(1)

def send_note(client, port):
    event1 = NoteOnEvent(note=60, velocity=64, channel=0)
    client.event_output(event1)
    client.drain_output()
    time.sleep(1)
    event2 = NoteOffEvent(note=60, channel=0)
    client.event_output(event2)
    client.drain_output()

def run_metronome_and_listnener():
    listenerThread = Thread(target=event_listener)
    listenerThread.start()
    time.sleep(1)
    metronomeThread = Thread(target=metronome)
    metronomeThread.start()
    
    listenerThread.join()
    metronomeThread.join()

def main():
    with spawn_synth() as synth:
        connect_keyboard_to_synth()
        run_metronome_and_listnener()
        synth.terminate()
