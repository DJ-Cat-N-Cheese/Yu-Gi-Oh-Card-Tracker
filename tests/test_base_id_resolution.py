import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Mock nicegui
mock_ui = MagicMock()
sys.modules['nicegui'] = mock_ui
sys.modules['nicegui.ui'] = mock_ui

# Mock yaml
mock_yaml = MagicMock()
sys.modules['yaml'] = mock_yaml

# Mock pydantic
class MockBaseModel:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)
    @classmethod
    def model_validate(cls, obj):
        return obj

mock_pydantic = MagicMock()
mock_pydantic.BaseModel = MockBaseModel
sys.modules['pydantic'] = mock_pydantic

# Mock requests
mock_requests = MagicMock()
sys.modules['requests'] = mock_requests

# Mock aiohttp
mock_aiohttp = MagicMock()
sys.modules['aiohttp'] = mock_aiohttp

# Mock PIL
mock_pil = MagicMock()
sys.modules['PIL'] = mock_pil
sys.modules['PIL.Image'] = mock_pil.Image

# Mock bs4
mock_bs4 = MagicMock()
sys.modules['bs4'] = mock_bs4

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to mock models before they are imported if they use pydantic in a way that breaks
# But wait, src.core.models imports pydantic.
# Let's try to mock the models themselves or just provide enough of pydantic.

from src.core.models import Deck, ApiCard, Collection, CollectionCard

from src.ui.deck_builder import DeckBuilderPage

class TestBaseIdResolution(unittest.TestCase):
    def setUp(self):
        # Patch dependencies
        self.persistence_patcher = patch('src.ui.deck_builder.persistence')
        self.persistence_mock = self.persistence_patcher.start()
        self.persistence_mock.load_ui_state.return_value = {}
        self.persistence_mock.list_decks.return_value = []
        self.persistence_mock.list_collections.return_value = []

        self.config_patcher = patch('src.ui.deck_builder.config_manager')
        self.config_mock = self.config_patcher.start()
        self.config_mock.get_deck_builder_page_size.return_value = 50

        # Create page instance
        self.page = DeckBuilderPage()

        # Setup alt_art_map: 101 is alt art of 1
        self.page.alt_art_map = {101: 1}
        # Mock api_card_map
        card1 = MagicMock(spec=ApiCard)
        card1.id = 1
        card1.name = "Card 1"
        self.page.api_card_map = {1: card1}

    def tearDown(self):
        self.persistence_patcher.stop()
        self.config_patcher.stop()

    def test_calculate_genesys_points_resolution(self):
        self.page.state['current_deck'] = Deck(main=[1, 101], extra=[], side=[])
        self.page.state['current_banlist_type'] = 'genesys'
        self.page.state['current_banlist_map'] = {'1': '5'} # Point for base ID

        points = self.page.calculate_genesys_points()
        # Should be 5 + 5 = 10 because 101 resolves to 1
        self.assertEqual(points, 10)

    def test_check_violations_resolution(self):
        self.page.state['current_deck'] = Deck(main=[101, 101], extra=[], side=[])
        self.page.state['current_banlist_type'] = 'classical'
        self.page.state['current_banlist_map'] = {'1': 'Limited'} # Limit 1 for base ID

        # global_usage uses calculate_global_usage which already resolved IDs
        violations = self.page.check_violations()
        self.assertTrue(violations['global'])
        self.assertTrue(violations['main'])

    def test_calculate_deck_counts_resolution(self):
        self.page.state['current_deck'] = Deck(main=[1, 101], extra=[1], side=[])
        counts = self.page.calculate_deck_counts()
        # Should have {1: 3} instead of {1: 2, 101: 1}
        self.assertEqual(counts.get(1), 3)
        self.assertNotIn(101, counts)

    def test_calculate_missing_deck_resolution(self):
        self.page.state['current_deck'] = Deck(main=[1, 101], extra=[], side=[])
        # Mock _get_filtered_owned_map to return 1 copy of ID 1
        with patch.object(self.page, '_get_filtered_owned_map', return_value={1: 1}):
            missing = self.page.calculate_missing_deck()
            # 1 copy of Base 1 is owned.
            # Deck has 1 and 101 (both Base 1).
            # One should be marked as owned, one missing.
            self.assertEqual(len(missing.main), 1)
            # It preserves original ID if missing
            self.assertEqual(missing.main[0], 101)

if __name__ == '__main__':
    unittest.main()
