import unittest
from unittest.mock import MagicMock
import sys

# Mock dependencies before importing pipeline
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['langdetect'] = MagicMock()
sys.modules['easyocr'] = MagicMock()
sys.modules['torch'] = MagicMock()
sys.modules['paddleocr'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()

# We also need to mock src.services.scanner.models
sys.modules['src.services.scanner.models'] = MagicMock()

from src.services.scanner.pipeline import CardScanner
# We need to re-import or reload if it was already imported, but since this is a fresh run it's fine.
# However, inside pipeline.py, it tries to import from local scope.

class TestPaddleConfig(unittest.TestCase):
    def test_paddle_init_config(self):
        # We need to ensure PaddleOCR is mocked where it is USED.
        # Since we mocked sys.modules['paddleocr'], the import inside pipeline.py
        # "from paddleocr import PaddleOCR" will get the mock.

        # We can get the mocked class from sys.modules
        MockPaddleOCR = sys.modules['paddleocr'].PaddleOCR

        scanner = CardScanner()
        scanner.get_paddleocr()

        # Verify PaddleOCR was called with enable_mkldnn=False
        args, kwargs = MockPaddleOCR.call_args
        self.assertIn('enable_mkldnn', kwargs)
        self.assertFalse(kwargs['enable_mkldnn'], "enable_mkldnn should be False")
        self.assertTrue(kwargs.get('use_angle_cls'), "use_angle_cls should be True")
        self.assertEqual(kwargs.get('lang'), 'en', "lang should be 'en'")

if __name__ == '__main__':
    unittest.main()
