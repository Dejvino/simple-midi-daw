import subprocess
from threading import Thread

from .midi import create_client, find_synth_port, find_keyboard_port, send_panic_event_to_synth

def get_port_address(port_info):
    return "{}:{}".format(port_info.client_id, port_info.port_id)

def spawn_player(synth_port, file):
    print("Spawning MIDI player from " + file)
    player = subprocess.Popen(["aplaymidi", "-p", get_port_address(synth_port), file])
    return player

def spawn_loop(synth_port, file):
    class LoopThread(Thread):
        def run(self):
            self.active = True
            while self.active:
                self.process = spawn_player(synth_port, file)
                self.process.wait()
        def terminate(self):
            self.active = False
            self.process.kill()
    t = LoopThread()
    t.start()
    return t

def spawn_recorder(kbd_port, file):
    print("Spawning MIDI recorder into " + file)
    recorder = subprocess.Popen(["arecordmidi", "-p", get_port_address(kbd_port), file])
    return recorder


class Playback:
    def __init__(self, inbox):
        self.inbox = inbox
        self.active = True
        self.process = None
        self.file = "recording.mid"

    def run(self):
        self.client = create_client("playback")
        while self.active:
            self.check_inbox()

    def check_inbox(self):
        while self.inbox:
            msg = self.inbox.popleft()
            self.on_message(msg)
    
    def on_message(self, msg):
        # TODO: switch msg type
        print("Message in playback: " + repr(msg))
        if (msg == "exit"):
            self.active = False
        elif (msg == "play"):
            self.on_play()
        elif (msg == "record"):
            self.on_record()
        elif (msg == "stop"):
            self.on_stop()
        elif (msg == "loop"):
            self.on_loop()
        else:
            print("Unknown playback message: " + repr(msg))
        
    def on_play(self):
        print("Playback: PLAY")
        if (self.process == None):
            synth_port = find_synth_port(self.client)
            self.process = spawn_player(synth_port, self.file)

    def on_stop(self):
        print("Playback: STOP")
        if (self.process != None):
            self.process.terminate()
            self.process = None
            print("Playback process stopped.")
        send_panic_event_to_synth()

    def on_record(self):
        print("Playback: REC")
        if (self.process == None):
            kbd_port = find_keyboard_port()
            self.process = spawn_recorder(kbd_port, self.file)

    def on_loop(self):
        print("Playback: LOOP")
        if (self.process == None):
            synth_port = find_synth_port(self.client)
            self.process = spawn_loop(synth_port, self.file)
