import unittest
import sys
import os
from unittest.mock import MagicMock, patch

# Ensure src is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mocking modules
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()
sys.modules['langdetect'] = MagicMock()
sys.modules['easyocr'] = MagicMock()
sys.modules['doctr'] = MagicMock()
sys.modules['doctr.io'] = MagicMock()
sys.modules['doctr.models'] = MagicMock()

from src.services.scanner.pipeline import CardScanner
from src.services.scanner.models import OCRResult

class TestScannerNewFeatures(unittest.TestCase):
    def setUp(self):
        # Suppress logging
        import logging
        logging.getLogger('src.services.scanner.pipeline').setLevel(logging.CRITICAL)
        self.scanner = CardScanner()

    def test_parse_stats(self):
        # Case 1: Standard
        text = "Some Text | ATK/1800 | DEF/1200 | More Text"
        atk, def_val = self.scanner._parse_stats(text)
        self.assertEqual(atk, "1800")
        self.assertEqual(def_val, "1200")

        # Case 2: Spaces
        text = "ATK / 2500 DEF /  2100"
        atk, def_val = self.scanner._parse_stats(text)
        self.assertEqual(atk, "2500")
        self.assertEqual(def_val, "2100")

        # Case 3: Question Marks
        text = "ATK/?"
        atk, def_val = self.scanner._parse_stats(text)
        self.assertEqual(atk, "?")

        # Case 4: No stats
        text = "Spell Card"
        atk, def_val = self.scanner._parse_stats(text)
        self.assertIsNone(atk)
        self.assertIsNone(def_val)

    @patch('src.services.scanner.pipeline.CardScanner.ocr_scan')
    def test_detect_first_edition(self, mock_ocr):
        dummy_img = MagicMock()
        # Mock subscripting to return something
        dummy_img.__getitem__.return_value = MagicMock()

        # Mock OCR output behavior
        def side_effect(image, engine='easyocr', scope='full'):
            return OCRResult(engine=engine, raw_text=mock_ocr.return_value.raw_text)
        mock_ocr.side_effect = side_effect

        # Test 1: Marker Present ("1st Edition")
        mock_ocr.return_value = OCRResult(engine='easyocr', raw_text="1st Edition")
        self.assertTrue(self.scanner.detect_first_edition(dummy_img))

        # Test 2: Marker Present ("LIMITED EDITION")
        mock_ocr.return_value = OCRResult(engine='easyocr', raw_text="LIMITED EDITION")
        self.assertTrue(self.scanner.detect_first_edition(dummy_img))

        # Test 3: Keyword Only (Short text -> Valid)
        mock_ocr.return_value = OCRResult(engine='easyocr', raw_text="Edition")
        self.assertTrue(self.scanner.detect_first_edition(dummy_img))

        # Test 4: Keyword Only (Long text -> Invalid/Suspicious)
        mock_ocr.return_value = OCRResult(engine='easyocr', raw_text="This card cannot be used in a Duel. The Edition of this card is special.")
        self.assertFalse(self.scanner.detect_first_edition(dummy_img))

        # Test 5: Keyword Only (Long text) BUT Marker Present -> Valid
        mock_ocr.return_value = OCRResult(engine='easyocr', raw_text="This card is 1st Edition and cannot be used.")
        self.assertTrue(self.scanner.detect_first_edition(dummy_img))

        # Test 6: Localized ("Auflage")
        mock_ocr.return_value = OCRResult(engine='easyocr', raw_text="1. Auflage")
        self.assertTrue(self.scanner.detect_first_edition(dummy_img))

if __name__ == '__main__':
    unittest.main()
