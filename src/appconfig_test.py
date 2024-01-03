import unittest

from src.appconfig import load_common, load_keyboards

class appconfigTest(unittest.TestCase):
    def test_load_common(self):
        config = load_common()
        self.assertEqual(config['metronome']['bpm'], '120')

    def test_load_keyboards(self):
        config = load_keyboards()
        self.assertEqual(config['description']['client_name'], 'Launchkey MK3 37')
