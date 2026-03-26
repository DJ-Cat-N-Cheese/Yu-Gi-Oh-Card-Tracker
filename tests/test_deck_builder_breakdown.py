import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import sys
import os

sys.path.append(os.getcwd())

# Mock modules globally before import
sys.modules['nicegui'] = MagicMock()
sys.modules['yaml'] = MagicMock()
sys.modules['requests'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()
sys.modules['numpy'] = MagicMock()
sys.modules['orjson'] = MagicMock()

# Now import the class under test
from src.ui.deck_builder import DeckBuilderPage
from src.core.models import Collection, CollectionCard, CollectionVariant

class TestDeckBuilderBreakdown(unittest.IsolatedAsyncioTestCase):
    async def test_open_deck_builder_wrapper_breakdown(self):
        # Mock dependencies used in __init__
        with patch('src.ui.deck_builder.persistence') as mock_persistence, \
             patch('src.ui.deck_builder.SingleCardView') as MockSingleCardView:

            # Setup mock persistence
            mock_persistence.load_ui_state.return_value = {}
            mock_persistence.list_decks.return_value = []
            mock_persistence.list_collections.return_value = []

            # Instantiate
            page = DeckBuilderPage()

            # Verify mocks were used
            mock_persistence.load_ui_state.assert_called()

            # Mock the single_card_view instance created in __init__
            page.single_card_view = MagicMock()
            page.single_card_view.open_deck_builder = AsyncMock()

            # Setup Reference Collection
            v1 = MagicMock()
            v1.set_code = "SET-A"
            v1.rarity = "Common"
            v1.total_quantity = 2
            e1 = MagicMock()
            e1.quantity = 2
            e1.storage_location = "Binder 1"
            v1.entries = [e1]

            v2 = MagicMock()
            v2.set_code = "SET-A"
            v2.rarity = "Common"
            v2.total_quantity = 1
            e2 = MagicMock()
            e2.quantity = 1
            e2.storage_location = None
            v2.entries = [e2]

            v3 = MagicMock()
            v3.set_code = "SET-B"
            v3.rarity = "Ultra"
            v3.total_quantity = 5
            e3 = MagicMock()
            e3.quantity = 3
            e3.storage_location = "Box A"
            e4 = MagicMock()
            e4.quantity = 2
            e4.storage_location = "Box A"
            v3.entries = [e3, e4]

            c_card = MagicMock(spec=CollectionCard)
            c_card.card_id = 123
            c_card.variants = [v1, v2, v3]

            ref_col = MagicMock(spec=Collection)
            ref_col.cards = [c_card]

            page.state['reference_collection'] = ref_col

            # Input Card
            api_card = MagicMock()
            api_card.id = 123

            # Action
            await page.open_deck_builder_wrapper(api_card)

            # Verify
            page.single_card_view.open_deck_builder.assert_called_once()
            args, _ = page.single_card_view.open_deck_builder.call_args

            passed_card = args[0]
            passed_count = args[2]
            passed_breakdown = args[3]

            self.assertEqual(passed_card, api_card)
            self.assertEqual(passed_count, 8)

            expected_breakdown = {
            "SET-A (Common)": {
                'total': 3,
                'locations': {
                    'Binder 1': 2,
                    'Unsorted': 1
                }
            },
            "SET-B (Ultra)": {
                'total': 5,
                'locations': {
                    'Box A': 5
                }
            }
            }
            self.assertEqual(passed_breakdown, expected_breakdown)

if __name__ == '__main__':
    unittest.main()
