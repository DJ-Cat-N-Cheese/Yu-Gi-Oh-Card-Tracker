
import sys
import unittest
from unittest.mock import MagicMock, patch
import time
import os

# Add current directory to path so src can be imported
sys.path.append(os.getcwd())

# Mock dependencies not available in test env
# These must be mocked BEFORE importing src.services.scanner.manager
sys.modules['cv2'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['nicegui'] = MagicMock()
sys.modules['fastapi'] = MagicMock()
sys.modules['src.services.ygo_api'] = MagicMock()
sys.modules['src.services.image_manager'] = MagicMock()

# Mock SCANNER_AVAILABLE to True for testing logic
with patch('src.services.scanner.SCANNER_AVAILABLE', True):
    from src.services.scanner import manager

class MockScanner:
    def find_card_contour(self, frame):
        time.sleep(0.2) # Simulate processing time to catch status change
        return [[0,0], [100,0], [100,100], [0,100]]
    def warp_card(self, frame, contour):
        return frame
    def debug_draw_rois(self, frame):
        return frame
    def get_fallback_crop(self, frame):
        return frame
    def ocr_scan(self, frame, engine='easyocr'):
        return {'set_id': 'TEST-001', 'set_id_conf': 99.9, 'language': 'en', 'raw_text': 'TEST'}
    def detect_rarity_visual(self, frame):
        return 'Common'
    def detect_first_edition(self, frame):
        return True
    def match_artwork(self, *args):
        return None, 0
    # Add other missing methods if needed
    def find_card_yolo(self, frame):
        return [[0,0], [100,0], [100,100], [0,100]]

class TestScannerManagerLogic(unittest.TestCase):
    def setUp(self):
        # Patch dependencies within the manager module
        self.patchers = [
            patch('src.services.scanner.manager.CardScanner', MockScanner),
            patch('src.services.scanner.manager.SCANNER_AVAILABLE', True),
            # Mock run.io_bound to execute synchronously
            patch('src.services.scanner.manager.run.io_bound', side_effect=lambda f, *args: f(*args)),
            patch('src.services.scanner.manager.ygo_service', MagicMock()),
            patch('src.services.scanner.manager.cv2', MagicMock()),
            patch('src.services.scanner.manager.np', MagicMock())
        ]
        for p in self.patchers:
            p.start()

        # Reset the singleton if needed or create a new instance
        # Since scanner_manager is global, we can test it directly or instantiate a new one
        # Instantiating a new one is safer for isolation
        self.manager = manager.ScannerManager()
        self.manager.start()

    def tearDown(self):
        self.manager.stop()
        for p in self.patchers:
            p.stop()

    def test_status_flow(self):
        """Test that status transitions correctly from Paused -> Idle -> Processing -> Idle."""
        # Initial State: Should be Paused because logic defaults to paused=True
        # And the worker loop sets status to "Paused" if paused=True
        time.sleep(0.2) # Allow worker to run once
        self.assertTrue(self.manager.paused)
        self.assertEqual(self.manager.get_status(), "Paused")

        # Resume
        self.manager.resume()
        self.assertFalse(self.manager.paused)

        # Should transition to Idle
        time.sleep(0.2)
        self.assertEqual(self.manager.get_status(), "Idle")

        # Submit Scan
        options = {"tracks": ["easyocr"], "preprocessing": "classic"}
        # Mock imdecode to return a valid frame
        with patch('src.services.scanner.manager.cv2.imdecode', return_value="FAKE_FRAME"):
            self.manager.submit_scan(b"data", options, label="Test")

            # Status should become Processing
            # We poll until we see Processing or it finishes
            status_seen = []
            start_time = time.time()
            while time.time() - start_time < 2:
                s = self.manager.get_status()
                status_seen.append(s)
                # If we see Processing, we are good, but we wait for it to finish to verify full cycle
                if "Processing" in s:
                    pass
                if s == "Idle" and len(self.manager.get_queue_snapshot()) == 0 and any("Processing" in st for st in status_seen):
                    break
                time.sleep(0.05)

            # Verify we saw Processing
            self.assertTrue(any("Processing" in s for s in status_seen), f"Did not see Processing state. Status history: {status_seen}")

            # Verify final state is Idle
            self.assertEqual(self.manager.get_status(), "Idle")

            # Verify logs contain "Finished"
            logs = self.manager.debug_state['logs']
            self.assertTrue(any("Finished" in l for l in logs), f"Logs do not contain Finished. Logs: {logs}")

if __name__ == '__main__':
    unittest.main()
