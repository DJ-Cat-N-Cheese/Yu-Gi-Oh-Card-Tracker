import unittest
from unittest.mock import MagicMock, patch, mock_open
import json
import os
import sys

# Ensure src in path
sys.path.append(os.getcwd())

# Mock all dependencies that might be missing
sys.modules['numpy'] = MagicMock()
import numpy as np
sys.modules['cv2'] = MagicMock()
import cv2
sys.modules['nicegui'] = MagicMock()
sys.modules['pydantic'] = MagicMock()
sys.modules['langdetect'] = MagicMock()
sys.modules['easyocr'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()
sys.modules['doctr'] = MagicMock()
sys.modules['doctr.io'] = MagicMock()
sys.modules['doctr.models'] = MagicMock()
sys.modules['src.services.scanner.pipeline'] = MagicMock()
sys.modules['src.services.scanner.models'] = MagicMock()
sys.modules['src.services.ygo_api'] = MagicMock()
sys.modules['src.services.image_manager'] = MagicMock()
sys.modules['src.core.utils'] = MagicMock()

from src.services.scanner.manager import ScannerManager

class TestScannerSecurityFix(unittest.TestCase):
    def test_art_index_json_serialization(self):
        manager = ScannerManager()
        manager.scanner = MagicMock()

        # Create a dummy index with something that looks like a numpy array
        mock_array = MagicMock()
        mock_array.tolist.return_value = [0.1, 0.2, 0.3]
        manager.art_index = {"test_image.jpg": mock_array}

        # Mock os.path.join and open
        with patch('os.path.join', return_value="dummy_path.json"), \
             patch('builtins.open', mock_open()) as mocked_file, \
             patch('json.dump') as mock_json_dump, \
             patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=['test_image.jpg']), \
             patch('cv2.imread', return_value=np.zeros((10,10,3))):

            # Mock extract_yolo_features to return a feature
            manager.scanner.extract_yolo_features.return_value = mock_array

            manager._build_art_index(force=True)

            # Check if json.dump was called with correct data
            mock_json_dump.assert_called_once()
            args, _ = mock_json_dump.call_args
            self.assertEqual(args[0], {"test_image.jpg": [0.1, 0.2, 0.3]})

    def test_art_index_json_deserialization(self):
        manager = ScannerManager()
        manager.scanner = MagicMock()

        json_data = '{"test_image.jpg": [0.1, 0.2, 0.3]}'

        with patch('os.path.join', return_value="dummy_path.json"), \
             patch('os.path.exists', side_effect=lambda x: x == "dummy_path.json"), \
             patch('builtins.open', mock_open(read_data=json_data)), \
             patch('json.load', return_value={"test_image.jpg": [0.1, 0.2, 0.3]}):

            # We want to trigger the load part of _build_art_index
            manager.art_index = {} # Ensure it's empty
            manager._build_art_index(force=False)

            self.assertIn("test_image.jpg", manager.art_index)
            # Since we mocked numpy, np.array([0.1, 0.2, 0.3]) will be a MagicMock
            self.assertTrue(isinstance(manager.art_index["test_image.jpg"], MagicMock))

if __name__ == '__main__':
    unittest.main()
