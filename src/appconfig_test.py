import unittest

from src.appconfig import load_keyboards

class appconfigTest(unittest.TestCase):
    def test_load_keyboards(self):
        config = load_keyboards()
        self.assertEqual(config['description']['client_name'], 'Launchkey MK3 37')
