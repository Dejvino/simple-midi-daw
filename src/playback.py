import subprocess

def spawn_player(synth_port, file):
    print("Spawning MIDI player from " + file)
    player = subprocess.Popen(["aplaymidi", "-p", synth_port, file])
    return player

def spawn_recorder(kbd_port, file):
    print("Spawning MIDI recorder into " + file)
    recorder = subprocess.Popen(["arecordmidi", "-p", kbd_port, file])
    return recorder

class Playback:
    def __init__(self, inbox):
        self.inbox = inbox
        self.active = True

    def run(self):
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
        else:
            print("Unknown playback message: " + repr(msg))
        
    def on_play(self):
        print("Playback: PLAY")

    def on_stop(self):
        print("Playback: STOP")

    def on_record(self):
        print("Playback: REC")
        