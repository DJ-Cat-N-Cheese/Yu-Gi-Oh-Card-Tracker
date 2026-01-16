import sys
import os
import asyncio
import unittest
from unittest.mock import MagicMock, patch
import json
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.services.ygo_api import ygo_service
from src.services.sample_generator import generate_sample_collection
from src.core.models import ApiCard, Collection
from src.core.persistence import persistence

class TestSettingsFunctions(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        # Ensure we have a clean state if needed
        pass

    async def test_fetch_card_database(self):
        """Test fetching and parsing card database."""
        logger.info("Testing fetch_card_database...")

        # Mock requests.get to avoid hitting real API and to provide controlled data
        mock_response = MagicMock()
        mock_response.status_code = 200

        # Create a sample API response
        sample_data = {
            "data": [
                {
                    "id": 12345,
                    "name": "Test Card",
                    "type": "Normal Monster",
                    "frameType": "normal",
                    "desc": "A test card.",
                    "card_images": [
                        {
                            "id": 12345,
                            "image_url": "http://example.com/12345.jpg",
                            "image_url_small": "http://example.com/12345_small.jpg"
                        }
                    ],
                    "card_sets": [
                        {
                            "set_name": "Test Set",
                            "set_code": "TEST-EN001",
                            "set_rarity": "Common",
                            "set_price": "1.00"
                        }
                    ]
                }
            ]
        }
        mock_response.json.return_value = sample_data

        with patch('requests.get', return_value=mock_response):
            # We also mock _save_db_file to avoid writing to disk during test (optional, but cleaner)
            with patch.object(ygo_service, '_save_db_file') as mock_save:
                count = await ygo_service.fetch_card_database("en")

                self.assertEqual(count, 1)
                self.assertEqual(len(ygo_service._cards_cache["en"]), 1)
                card = ygo_service._cards_cache["en"][0]
                self.assertIsInstance(card, ApiCard)
                self.assertEqual(card.name, "Test Card")

                # Check if variant_id was generated
                self.assertEqual(len(card.card_sets), 1)
                self.assertIsNotNone(card.card_sets[0].variant_id)
                logger.info(f"Verified variant_id generation: {card.card_sets[0].variant_id}")

    async def test_generate_sample_collection(self):
        """Test generating a sample collection."""
        logger.info("Testing generate_sample_collection...")

        # We need a card database for this to work.
        # Let's manually populate the cache so we don't need network
        mock_card = ApiCard(
            id=55555,
            name="Sample Gen Card",
            type="Effect Monster",
            frameType="effect",
            desc="Effect",
            card_images=[
                 {
                    "id": 55555,
                    "image_url": "http://example.com/55555.jpg",
                    "image_url_small": "http://example.com/55555_small.jpg"
                }
            ],
            card_sets=[
                {
                    "set_name": "Sample Set",
                    "set_code": "SMPL-EN001",
                    "set_rarity": "Ultra Rare",
                    "set_price": "10.00",
                    "variant_id": "test-variant-id"
                }
            ]
        )
        ygo_service._cards_cache["en"] = [mock_card]

        # Mock random.choice/sample to be deterministic or just let it run?
        # Let it run, but we need to ensure it picks our card.
        # Since we only have 1 card in DB, it must pick it.

        # We need to mock persistence.save_collection to avoid writing to disk
        # AND to verify the structure it tried to save.
        with patch('src.core.persistence.persistence.save_collection') as mock_save:
            # We also need to mock list_collections so it doesn't try to scan disk for filenames
            with patch('src.core.persistence.persistence.list_collections', return_value=[]):

                filename = await generate_sample_collection()

                self.assertEqual(filename, "sample_collection.json")

                # Verify arguments passed to save_collection
                mock_save.assert_called_once()
                args, _ = mock_save.call_args
                collection: Collection = args[0]

                self.assertIsInstance(collection, Collection)
                self.assertEqual(collection.name, "Sample Collection")
                self.assertTrue(len(collection.cards) > 0)

                # Check hierarchy
                c_card = collection.cards[0]
                self.assertEqual(c_card.name, "Sample Gen Card")
                self.assertTrue(len(c_card.variants) > 0)

                variant = c_card.variants[0]
                # self.assertEqual(variant.set_code, "SMPL-EN001") # Might be transformed, but usually EN->EN matches
                self.assertTrue(variant.set_code.startswith("SMPL-"))
                self.assertTrue(len(variant.entries) > 0)

                entry = variant.entries[0]
                self.assertIn(entry.condition, ["Mint", "Near Mint", "Played", "Damaged"])

                logger.info("Successfully verified generated collection structure.")

    async def test_download_all_images(self):
        """Test download all images logic."""
        logger.info("Testing download_all_images...")

        # Populate cache
        mock_card = ApiCard(
            id=999,
            name="Img Card",
            type="Spell",
            frameType="spell",
            desc="Spell",
            card_images=[
                 {
                    "id": 999,
                    "image_url": "http://high.res/img.jpg",
                    "image_url_small": "http://low.res/img.jpg"
                }
            ]
        )
        ygo_service._cards_cache["en"] = [mock_card]

        # Mock image_manager.download_batch
        with patch('src.services.image_manager.image_manager.download_batch', new_callable=MagicMock) as mock_download:
             # Make it awaitable
             f = asyncio.Future()
             f.set_result(None)
             mock_download.return_value = f

             await ygo_service.download_all_images(language="en")

             mock_download.assert_called_once()
             args, _ = mock_download.call_args
             url_map = args[0]

             self.assertIn(999, url_map)
             self.assertEqual(url_map[999], "http://low.res/img.jpg")

             # Test High Res
             # Reset mock
             f2 = asyncio.Future()
             f2.set_result(None)
             mock_download.return_value = f2
             mock_download.reset_mock()

             await ygo_service.download_all_images_high_res(language="en")

             mock_download.assert_called_once()
             args, kwargs = mock_download.call_args
             url_map = args[0]
             self.assertEqual(url_map[999], "http://high.res/img.jpg")
             self.assertTrue(kwargs.get('high_res'))

             logger.info("Successfully verified image download logic.")

if __name__ == '__main__':
    unittest.main()
