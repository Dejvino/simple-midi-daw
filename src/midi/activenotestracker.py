import mido

class ActiveNotesTracker:
    def __init__(self):
        self.notes={}

    def consume_midi_event(self, event):
        if event.note in self.notes:
            del self.notes[event.note]
        else:
            self.notes[event.note] = event

    def get_active_notes(self):
        return self.notes

    def get_note_offs(self):
        active_notes = self.get_active_notes()
        offs = {}
        for note in active_notes:
            note_on = active_notes[note]
            note_off = mido.Message("note_off", channel=note_on.channel, note=note_on.note)
            offs[note] = note_off
        return offs
