import unittest
from unittest.mock import MagicMock, patch, mock_open
import numpy as np
import os
import sys

# Ensure src in path
sys.path.append(os.getcwd())

# Mock modules if missing
from unittest.mock import MagicMock
sys.modules['langdetect'] = MagicMock()
sys.modules['easyocr'] = MagicMock()
sys.modules['keras_ocr'] = MagicMock()
sys.modules['doctr'] = MagicMock()
sys.modules['doctr.io'] = MagicMock()
sys.modules['doctr.models'] = MagicMock()
sys.modules['mmocr'] = MagicMock()
sys.modules['mmocr.apis'] = MagicMock()

# Ensure we have a YOLO class in pipeline even if import failed
# We can inject it into the module manually if we want, or just ensure import succeeds by mocking dependencies.
# If ultralytics is present, it imports.
# If langdetect is missing, the whole block fails.
# By mocking langdetect, the block should succeed (assuming ultralytics is installed).
# I installed ultralytics, numpy, cv2 earlier.

from src.services.scanner.pipeline import CardScanner
from src.services.scanner.manager import ScannerManager
from src.services.scanner.models import ScanDebugReport

class TestScannerArtMatch(unittest.TestCase):
    def setUp(self):
        self.yolo_patcher = patch('src.services.scanner.pipeline.YOLO')
        self.MockYOLO = self.yolo_patcher.start()

    def tearDown(self):
        self.yolo_patcher.stop()

    def test_calculate_similarity(self):
        scanner = CardScanner()
        v1 = np.array([1.0, 0.0, 0.0])
        v2 = np.array([1.0, 0.0, 0.0])
        self.assertAlmostEqual(scanner.calculate_similarity(v1, v2), 1.0)

        v3 = np.array([0.0, 1.0, 0.0])
        self.assertAlmostEqual(scanner.calculate_similarity(v1, v3), 0.0)

        v4 = np.array([-1.0, 0.0, 0.0])
        self.assertAlmostEqual(scanner.calculate_similarity(v1, v4), -1.0)

    def test_extract_features_calls_yolo(self):
        scanner = CardScanner()
        img = np.zeros((100, 100, 3), dtype=np.uint8)

        # Just verify it attempts to load model and run inference
        # Since we mock YOLO, the hook logic won't trigger, so it returns None
        res = scanner.extract_yolo_features(img, model_name='yolo26n-cls.pt')

        self.MockYOLO.assert_called_with('yolo26n-cls.pt')
        # Check if called
        self.MockYOLO.return_value.assert_called()

    @patch('src.services.scanner.manager.ScannerManager.get_debug_snapshot', return_value={})
    def test_manager_build_index(self, mock_snap):
        manager = ScannerManager()
        manager.scanner = MagicMock()

        # Mock extract to return a vector
        manager.scanner.extract_yolo_features.return_value = np.array([0.1, 0.2])

        # Mock filesystem
        with patch('os.listdir', return_value=['img1.jpg', 'img2.png', 'other.txt']), \
             patch('os.path.exists', return_value=True), \
             patch('cv2.imread', return_value=np.zeros((10,10,3))), \
             patch('builtins.open', mock_open()) as mocked_file, \
             patch('pickle.load', side_effect=Exception("No cache")), \
             patch('pickle.dump') as mock_dump:

             # Force empty index to trigger build
             manager.art_index = {}

             manager._build_art_index()

             # Verify results
             self.assertIn('img1.jpg', manager.art_index)
             self.assertIn('img2.png', manager.art_index)
             self.assertNotIn('other.txt', manager.art_index)
             self.assertEqual(len(manager.art_index), 2)

             # Verify dump called
             mock_dump.assert_called()

if __name__ == '__main__':
    unittest.main()
