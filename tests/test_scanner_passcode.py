import unittest
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.services.scanner.pipeline import CardScanner

class TestCardScannerPasscode(unittest.TestCase):
    def setUp(self):
        # Initialize scanner. It might try to load models/validation data,
        # but for _parse_passcode we don't need heavyweight dependencies loaded.
        self.scanner = CardScanner()

    def test_parse_passcode_clean(self):
        # 12345678 (8 digits)
        texts = ["Some Text", "ATK/2000 DEF/1500", "12345678", "More Text"]
        passcode = self.scanner._parse_passcode(texts)
        self.assertEqual(passcode, "12345678")

    def test_parse_passcode_typos(self):
        # 1234S678 -> 12345678 (S=5)
        texts = ["Some Text", "1234S678"]
        passcode = self.scanner._parse_passcode(texts)
        self.assertEqual(passcode, "12345678")

    def test_parse_passcode_typos_full_map(self):
        # S=5, I=1, O=0, Z=7, B=8, G=6, Q=0, D=0
        # Testing ZI0S B GQD
        # Z=7, I=1, 0=0, S=5, B=8, G=6, Q=0, D=0
        # 71058600
        texts = ["ZI0SBGQD"]
        passcode = self.scanner._parse_passcode(texts)
        self.assertEqual(passcode, "71058600")

    def test_parse_passcode_with_spaces(self):
        # 1234 5678
        texts = ["1234 5678"]
        passcode = self.scanner._parse_passcode(texts)
        self.assertEqual(passcode, "12345678")

    def test_parse_passcode_priority_bottom(self):
        # Should pick the last one
        texts = ["11111111", "Some Text", "22222222", "Footer"]
        passcode = self.scanner._parse_passcode(texts)
        self.assertEqual(passcode, "22222222")

    def test_parse_passcode_ignore_longer(self):
        # 123456789 (9 digits) should be ignored
        texts = ["123456789"]
        passcode = self.scanner._parse_passcode(texts)
        self.assertIsNone(passcode)

    def test_parse_passcode_ignore_shorter(self):
        # 1234567 (7 digits)
        texts = ["1234567"]
        passcode = self.scanner._parse_passcode(texts)
        self.assertIsNone(passcode)

    def test_parse_passcode_embedded(self):
        # "ID: 12345678"
        texts = ["ID: 12345678"]
        passcode = self.scanner._parse_passcode(texts)
        self.assertEqual(passcode, "12345678")

if __name__ == '__main__':
    unittest.main()
