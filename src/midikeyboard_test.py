import unittest

from src.midikeyboard import extract_row, build_sysex_message

class midikeyboardTest(unittest.TestCase):
    def test_extract_row(self):
        self.assertEqual(extract_row("abcd", 2), ("ab", "cd"))
        self.assertEqual(extract_row("a\nbcd", 3), ("a", "bcd"))
        self.assertEqual(extract_row("abcd\n", 3), ("abc", "d\n"))
        self.assertEqual(extract_row("a b c d", 2), ("a ", "b c d"))

    def test_build_sysex_message(self):
        config = {
            'sysex_0': 'hex:10 2F',
            'sysex_1': 'dec:10',
            'sysex_2': 'row',
            'sysex_3': 'message'
        }
        params = {
            'row': 5,
            'message': '\x30\x40'
        }
        result = build_sysex_message(config, params)
        self.assertEqual(result, b'\x10\x2F\x0A\x05\x30\x40')
