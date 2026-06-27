import sys
from unittest.mock import MagicMock, AsyncMock, patch
import unittest
from tests.mock_imports import import_with_module_mocks

# Mock nicegui modules before importing src.ui.bulk_add
nicegui_mock = MagicMock()
ui_mock = MagicMock()
run_mock = MagicMock()

# Mock dependencies
persistence_module_mock = MagicMock()
changelog_module_mock = MagicMock()
config_module_mock = MagicMock()
ygo_api_module_mock = MagicMock()
image_manager_module_mock = MagicMock()
collection_editor_module_mock = MagicMock()

bulk_add_module = import_with_module_mocks(
    'src.ui.bulk_add',
    {
        'nicegui': nicegui_mock,
        'nicegui.ui': ui_mock,
        'nicegui.run': run_mock,
        'src.core.persistence': persistence_module_mock,
        'src.core.changelog_manager': changelog_module_mock,
        'src.core.config': config_module_mock,
        'src.services.ygo_api': ygo_api_module_mock,
        'src.services.image_manager': image_manager_module_mock,
        'src.services.collection_editor': collection_editor_module_mock,
    },
)
BulkAddPage = bulk_add_module.BulkAddPage

class TestBulkAddFilterLogic(unittest.TestCase):
    def setUp(self):
        # Setup mock returns
        self.persistence_mock = persistence_module_mock.persistence
        self.persistence_mock.list_collections.return_value = []
        self.persistence_mock.load_ui_state.return_value = {}

        self.config_mock = config_module_mock.config_manager
        self.config_mock.get_language.return_value = 'EN'
        self.config_mock.get_bulk_add_page_size.return_value = 50

        with patch.object(bulk_add_module, 'SingleCardView'), \
             patch.object(bulk_add_module, 'StructureDeckDialog'), \
             patch.object(bulk_add_module, 'FilterPane'):
            self.page = BulkAddPage()

    def test_library_not_filtered_default(self):
        # Default state should be "Not Filtered"
        # Defaults: search='', set='', filter_card_type=['Monster', 'Spell', 'Trap']

        self.assertEqual(self.page.state['library_search_text'], '')
        self.assertEqual(self.page.state['filter_set'], '')
        self.assertEqual(self.page.state['filter_card_type'], ['Monster', 'Spell', 'Trap'])

        self.assertFalse(self.page.is_library_filtered())

    def test_library_filtered_by_text(self):
        self.page.state['library_search_text'] = 'Blue-Eyes'
        self.assertTrue(self.page.is_library_filtered())

    def test_library_filtered_by_set(self):
        self.page.state['filter_set'] = 'LOB'
        self.assertTrue(self.page.is_library_filtered())

    def test_library_filtered_by_type_narrow(self):
        self.page.state['filter_card_type'] = ['Monster']
        self.assertTrue(self.page.is_library_filtered())

    def test_library_filtered_by_type_wide(self):
        # Even if "wider" than default (e.g. including Skill), it counts as "Changed"
        self.page.state['filter_card_type'] = ['Monster', 'Spell', 'Trap', 'Skill']
        self.assertTrue(self.page.is_library_filtered())

    def test_collection_not_filtered_default(self):
        self.assertEqual(self.page.col_state['search_text'], '')
        self.assertFalse(self.page.is_collection_filtered())

    def test_collection_filtered(self):
        self.page.col_state['search_text'] = 'Dark Magician'
        self.assertTrue(self.page.is_collection_filtered())

    def test_collection_filtered_by_set(self):
        self.page.col_state['filter_set'] = 'SDK'
        self.assertTrue(self.page.is_collection_filtered())

if __name__ == '__main__':
    unittest.main()
