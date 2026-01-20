import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Mock nicegui
mock_ui = MagicMock()
sys.modules['nicegui'] = mock_ui
sys.modules['nicegui.ui'] = mock_ui
sys.modules['nicegui.run'] = MagicMock()
sys.modules['nicegui.run.io_bound'] = AsyncMock()

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.deck_builder import DeckBuilderPage
from src.core.models import Deck

class TestDeckUndoLogic(unittest.TestCase):
    def setUp(self):
        # Patch dependencies
        self.persistence_patcher = patch('src.ui.deck_builder.persistence')
        self.persistence_mock = self.persistence_patcher.start()
        self.persistence_mock.load_ui_state.return_value = {}
        self.persistence_mock.list_decks.return_value = []
        self.persistence_mock.list_collections.return_value = []

        self.changelog_patcher = patch('src.ui.deck_builder.changelog_manager')
        self.changelog_mock = self.changelog_patcher.start()

        self.config_patcher = patch('src.ui.deck_builder.config_manager')
        self.config_mock = self.config_patcher.start()
        self.config_mock.get_deck_builder_page_size.return_value = 50

        # Create page instance
        self.page = DeckBuilderPage()
        self.page.refresh_zone = MagicMock()
        self.page.update_zone_headers = MagicMock()
        self.page.render_header = MagicMock()
        self.page.save_current_deck = AsyncMock()

        # Set current deck
        self.deck = Deck(name="TestDeck")
        self.page.state['current_deck'] = self.deck
        self.page.state['current_deck_name'] = "TestDeck"

    def tearDown(self):
        self.persistence_patcher.stop()
        self.changelog_patcher.stop()
        self.config_patcher.stop()

    def test_undo_add(self):
        # Setup: Deck has card 123
        self.deck.main = [123]

        # Mock last change: ADD 123 to main
        self.changelog_mock.undo_last_change.return_value = {
            'action': 'ADD',
            'quantity': 1,
            'card_data': {'card_id': 123, 'target_zone': 'main'}
        }

        # Action
        asyncio.run(self.page.undo_last_action())

        # Assert
        self.assertEqual(self.deck.main, [])
        self.page.refresh_zone.assert_called_with('main')
        self.page.save_current_deck.assert_called()

    def test_undo_add_multiple(self):
        # Setup: Deck has 3 copies of 123
        self.deck.main = [123, 123, 123]

        # Mock last change: ADD 123 quantity 3
        self.changelog_mock.undo_last_change.return_value = {
            'action': 'ADD',
            'quantity': 3,
            'card_data': {'card_id': 123, 'target_zone': 'main'}
        }

        # Action
        asyncio.run(self.page.undo_last_action())

        # Assert
        self.assertEqual(self.deck.main, [])

    def test_undo_remove(self):
        # Setup: Deck empty
        self.deck.main = []

        # Mock last change: REMOVE 123 from main
        self.changelog_mock.undo_last_change.return_value = {
            'action': 'REMOVE',
            'quantity': 1,
            'card_data': {'card_id': 123, 'target_zone': 'main'}
        }

        # Action
        asyncio.run(self.page.undo_last_action())

        # Assert
        self.assertEqual(self.deck.main, [123])
        self.page.refresh_zone.assert_called_with('main')

    def test_undo_move(self):
        # Setup: Card 123 in Side (Moved from Main)
        self.deck.main = []
        self.deck.side = [123]

        # Mock last change: MOVE 123 from main to side
        self.changelog_mock.undo_last_change.return_value = {
            'action': 'MOVE',
            'quantity': 1,
            'card_data': {'card_id': 123, 'target_zone': 'side', 'from_zone': 'main'}
        }

        # Action
        asyncio.run(self.page.undo_last_action())

        # Assert
        self.assertEqual(self.deck.side, [])
        self.assertEqual(self.deck.main, [123])
        self.page.refresh_zone.assert_any_call('main')
        self.page.refresh_zone.assert_any_call('side')

if __name__ == '__main__':
    unittest.main()
