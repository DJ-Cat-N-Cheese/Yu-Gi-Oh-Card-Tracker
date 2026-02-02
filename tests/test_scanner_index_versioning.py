import unittest
from unittest.mock import MagicMock, patch, mock_open
import pickle
import sys
import os

# Ensure src in path
sys.path.append(os.getcwd())

# Mock modules
sys.modules['langdetect'] = MagicMock()
sys.modules['easyocr'] = MagicMock()
sys.modules['doctr'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()

from src.services.scanner.manager import ScannerManager

class TestScannerIndexVersioning(unittest.TestCase):

    def setUp(self):
        self.manager = ScannerManager()
        self.manager.scanner = MagicMock()
        self.manager.scanner.yolo_cls_model_name = 'yolo26n-cls.pt'
        self.manager.art_index = {}

    @patch('builtins.open', new_callable=mock_open)
    @patch('pickle.load')
    @patch('os.path.exists', return_value=True)
    def test_load_valid_index(self, mock_exists, mock_pickle, mock_file):
        # Setup: Valid cache with matching model
        cache_data = {
            "model_name": "yolo26n-cls.pt",
            "index": {"test.jpg": [0.1, 0.2]}
        }
        mock_pickle.return_value = cache_data

        self.manager._build_art_index()

        # Assert: Loaded successfully
        self.assertEqual(len(self.manager.art_index), 1)
        self.assertIn("test.jpg", self.manager.art_index)

    @patch('builtins.open', new_callable=mock_open)
    @patch('pickle.load')
    @patch('os.path.exists', return_value=True)
    def test_rebuild_on_model_mismatch(self, mock_exists, mock_pickle, mock_file):
        # Setup: Cache with DIFFERENT model
        cache_data = {
            "model_name": "yolo26l-cls.pt",
            "index": {"test.jpg": [0.1, 0.2]}
        }
        mock_pickle.return_value = cache_data

        # Mock listdir to simulate image folder so rebuild can "run" (though empty)
        with patch('os.listdir', return_value=[]):
            self.manager._build_art_index()

        # Assert: Index should be empty (because rebuild found no images in mocked listdir),
        # meaning it discarded the cache.
        self.assertEqual(len(self.manager.art_index), 0)

    @patch('builtins.open', new_callable=mock_open)
    @patch('pickle.load')
    @patch('os.path.exists', return_value=True)
    def test_rebuild_on_legacy_format(self, mock_exists, mock_pickle, mock_file):
        # Setup: Cache with old Dict format (no metadata)
        cache_data = {"test.jpg": [0.1, 0.2]}
        mock_pickle.return_value = cache_data

        with patch('os.listdir', return_value=[]):
            self.manager._build_art_index()

        # Assert: Discarded legacy cache
        self.assertEqual(len(self.manager.art_index), 0)

if __name__ == '__main__':
    unittest.main()
