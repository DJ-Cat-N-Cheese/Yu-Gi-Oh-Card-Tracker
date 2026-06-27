import sys
import os
import asyncio
import queue
from unittest.mock import MagicMock, patch
from tests.mock_imports import import_with_module_mocks

# Add project root to path
sys.path.append(os.getcwd())

# Mock modules that might be missing or heavy
cv2_mock = MagicMock()
pipeline_mock = MagicMock()

scanner_manager_module = import_with_module_mocks(
    'src.services.scanner.manager',
    {
        'cv2': cv2_mock,
        'src.services.scanner.pipeline': pipeline_mock,
    },
)
ScannerManager = scanner_manager_module.ScannerManager
from src.services.scanner.models import OCRResult

def test_image_id_propagation():
    asyncio.run(_test_image_id_propagation())


async def _test_image_id_propagation():
    print("Initializing ScannerManager...")
    manager = ScannerManager()

    # Mock find_best_match to return a candidate with image_id
    async def mock_find_best_match(*args, **kwargs):
        print("Mock find_best_match called")
        return {
            "ambiguity": False,
            "candidates": [{
                "name": "Test Card",
                "card_id": 12345,
                "set_code": "SRL-G021",
                "rarity": "Common",
                "score": 90.0,
                "image_id": 99999, # The ID we want to see propagated
                "variant_id": None
            }]
        }

    manager.find_best_match = mock_find_best_match

    # Mock ygo_service to avoid DB calls
    with patch.object(scanner_manager_module, 'ygo_service') as mock_ygo:
        # Mock get_card to return None so we skip image path resolution logic
        mock_ygo.get_card.return_value = None

        # Prepare lookup data
        lookup_data = {
            "ocr_result": {
                "engine": "test",
                "raw_text": "Test",
                "language": "EN"
            },
            "art_match": None
        }

        manager.lookup_queue.put(lookup_data)

        print("Processing pending lookups...")
        await manager.process_pending_lookups()

        try:
            result = manager.get_latest_result()
            print(f"Result keys: {result.keys() if result else 'None'}")

            if result and 'image_id' in result:
                print(f"SUCCESS: image_id found in result: {result['image_id']}")
                if result['image_id'] == 99999:
                    print("Verified value matches.")
                else:
                    print(f"Value mismatch. Expected 99999, got {result['image_id']}")
            else:
                print("FAILURE: image_id NOT found in result.")

        except queue.Empty:
            print("FAILURE: No result in queue.")

if __name__ == "__main__":
    test_image_id_propagation()
