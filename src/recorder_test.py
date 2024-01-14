import unittest
import mido

from src.recorder import ActiveNotesTracker

class ActiveNotesTrackerTest(unittest.TestCase):
    def test_get_active_notes_empty_initial(self):
        tracker = ActiveNotesTracker()
        self.assertEqual(tracker.get_active_notes(), {})

    def test_get_active_notes_one_added(self):
        tracker = ActiveNotesTracker()
        event = mido.Message("note_on", channel=1, note=60, velocity=30)
        tracker.consume_midi_event(event)
        self.assertEqual(tracker.get_active_notes(), {60: event})

    def test_get_active_notes_empty_after_note_off(self):
        tracker = ActiveNotesTracker()
        event = mido.Message("note_on", channel=1, note=60, velocity=30)
        tracker.consume_midi_event(mido.Message("note_on", channel=1, note=60, velocity=30))
        tracker.consume_midi_event(mido.Message("note_off", channel=1, note=60))
        self.assertEqual(tracker.get_active_notes(), {})
