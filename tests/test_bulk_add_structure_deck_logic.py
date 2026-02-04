import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import asyncio

# Mock NiceGUI
sys.modules['nicegui'] = MagicMock()
sys.modules['nicegui.ui'] = MagicMock()
sys.modules['nicegui.run'] = MagicMock()

from src.ui.bulk_add import BulkAddPage
from src.services.ygo_api import ApiCard, ApiCardSet
from src.core.models import ApiCardImage

class TestBulkAddStructureDeck(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.page = BulkAddPage()
        self.page.current_collection_obj = MagicMock()
        self.page.state['selected_collection'] = "test_col.json"

        # Mock Maps
        self.card1 = ApiCard(id=1001, name="Blue-Eyes White Dragon", type="Normal Monster", frameType="normal", desc="desc",
                             card_sets=[
                                 ApiCardSet(set_code="SDY-E001", set_rarity="Ultra Rare", image_id=1001, set_name="Set"),
                                 ApiCardSet(set_code="LOB-E001", set_rarity="Ultra Rare", image_id=1002, set_name="Set")
                             ],
                             card_images=[ApiCardImage(id=1001, image_url="url", image_url_small="url")])

        self.page.set_code_map = {
            "SDY-E001": self.card1,
            "LOB-E001": self.card1
        }
        self.page.name_map = {
            "blue-eyes white dragon": self.card1
        }

        self.page.open_structure_deck_preview_dialog = MagicMock()

    async def test_structure_deck_resolution_exact_match(self):
        cards = [
            {'set_code': 'SDY-E001', 'quantity': 1, 'rarity': 'Ultra Rare', 'name': 'Blue-Eyes White Dragon'}
        ]

        await self.page.process_structure_deck_add("Test Deck", cards)

        self.page.open_structure_deck_preview_dialog.assert_called_once()
        args = self.page.open_structure_deck_preview_dialog.call_args[0]
        items = args[1]

        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['status'], 'Ready')
        self.assertEqual(items[0]['set_code'], 'SDY-E001')

    async def test_structure_deck_resolution_name_fallback(self):
        # Set code unknown, but name known
        cards = [
            {'set_code': 'UNKNOWN-001', 'quantity': 1, 'rarity': 'Common', 'name': 'Blue-Eyes White Dragon'}
        ]

        await self.page.process_structure_deck_add("Test Deck", cards)

        items = self.page.open_structure_deck_preview_dialog.call_args[0][1]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['api_card'], self.card1)
        self.assertEqual(items[0]['status'], 'New Variant') # Because UNKNOWN-001 doesn't exist in card1 sets
        self.assertEqual(items[0]['set_code'], 'UNKNOWN-001')

    async def test_structure_deck_resolution_card_not_found(self):
        cards = [
            {'set_code': 'NONEXISTENT', 'quantity': 1, 'rarity': 'Common', 'name': 'Ghost Card'}
        ]

        await self.page.process_structure_deck_add("Test Deck", cards)

        items = self.page.open_structure_deck_preview_dialog.call_args[0][1]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['status'], 'Card Not Found')
        self.assertFalse(items[0]['include'])

if __name__ == '__main__':
    unittest.main()
