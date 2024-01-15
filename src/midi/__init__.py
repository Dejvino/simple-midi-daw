
from .activenotestracker import ActiveNotesTracker
from .client import MidiClient

class MidiEvent:
    def __init__(self, source_type, event):
        self.source_type = source_type
        self.event = event
