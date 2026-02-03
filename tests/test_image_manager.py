import unittest
import os
import shutil
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import sys

# Mock nicegui modules if not present
sys.modules['nicegui'] = MagicMock()
sys.modules['nicegui.run'] = MagicMock()

from src.services.image_manager import image_manager

class TestImageManagerPreservation(unittest.TestCase):
    def setUp(self):
        # Use a temporary directory for tests
        self.test_dir = "tests/data/images"
        self.test_sets_dir = "tests/data/sets"

        # Save original dirs
        self.orig_images_dir = image_manager.images_dir
        self.orig_sets_dir = image_manager.sets_dir

        # Set new dirs
        image_manager.images_dir = self.test_dir
        image_manager.sets_dir = self.test_sets_dir

        os.makedirs(self.test_dir, exist_ok=True)
        os.makedirs(self.test_sets_dir, exist_ok=True)

    def tearDown(self):
        # Restore dirs
        image_manager.images_dir = self.orig_images_dir
        image_manager.sets_dir = self.orig_sets_dir

        # Clean up
        if os.path.exists("tests/data"):
            shutil.rmtree("tests/data")

    def test_ensure_set_image_preserves_existing(self):
        set_code = "TESTSET"
        local_path = image_manager.get_set_image_path(set_code)

        # Create dummy existing file
        with open(local_path, "w") as f:
            f.write("existing")

        # Call ensure_set_image
        # We need to run async function
        path = asyncio.run(image_manager.ensure_set_image(set_code, "http://fake.url/img.jpg"))

        self.assertEqual(path, local_path)
        self.assertTrue(os.path.exists(local_path))
        with open(local_path, "r") as f:
            self.assertEqual(f.read(), "existing")

    def test_download_batch_preserves_existing(self):
        card_id = 12345
        local_path = image_manager.get_local_path(card_id)

        # Create dummy existing file
        with open(local_path, "w") as f:
            f.write("existing_card")

        # Mock _download_with_session to ensure it's not called
        image_manager._download_with_session = AsyncMock()

        url_map = {card_id: "http://fake.url/img.jpg"}

        asyncio.run(image_manager.download_batch(url_map))

        image_manager._download_with_session.assert_not_called()
        self.assertTrue(os.path.exists(local_path))
