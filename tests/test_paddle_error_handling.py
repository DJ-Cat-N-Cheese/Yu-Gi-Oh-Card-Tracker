import unittest
from unittest.mock import MagicMock
import sys

# Mock dependencies
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['langdetect'] = MagicMock()
sys.modules['easyocr'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['paddleocr'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()
sys.modules['src.services.scanner.models'] = MagicMock()

from src.services.scanner.pipeline import CardScanner

class TestPaddleErrorHandling(unittest.TestCase):
    def test_paddle_exception_propagation(self):
        """
        Verify that exceptions raised by PaddleOCR propagate out of ocr_scan
        instead of being swallowed. This ensures the caller (ScannerManager)
        can stop further attempts with the broken engine.
        """
        # Setup
        scanner = CardScanner()
        mock_ocr_instance = MagicMock()

        # Simulate an IndexError inside the ocr() call
        mock_ocr_instance.ocr.side_effect = IndexError("string index out of range")

        # Inject our mock into the scanner
        scanner.paddle_ocr = mock_ocr_instance

        mock_image = MagicMock()
        mock_image.shape = (100, 100, 3) # valid shape

        # Execute & Assert
        with self.assertRaises(IndexError) as cm:
            scanner.ocr_scan(mock_image, engine='paddle')

        self.assertEqual(str(cm.exception), "string index out of range")

if __name__ == '__main__':
    unittest.main()
