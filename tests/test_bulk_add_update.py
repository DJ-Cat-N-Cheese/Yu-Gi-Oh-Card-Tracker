import sys
from unittest.mock import MagicMock, AsyncMock, patch, call
import unittest
import asyncio
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
ygo_api_module_mock.ygo_service.ensure_card_variants = AsyncMock(return_value=1)
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
BulkCollectionEntry = bulk_add_module.BulkCollectionEntry

class TestBulkAddUpdate(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        # Setup mock returns
        self.persistence_mock = persistence_module_mock.persistence
        self.persistence_mock.list_collections.return_value = ['TestCol']
        self.persistence_mock.load_ui_state.return_value = {}

        self.collection_editor_mock = collection_editor_module_mock.CollectionEditor
        self.collection_editor_mock.reset_mock()
        self.changelog_manager_mock = changelog_module_mock.changelog_manager

        # Mock run.io_bound to execute immediately
        # Patch the 'run' imported in bulk_add
        self.run_patcher = patch.object(bulk_add_module, 'run')
        self.run_mock = self.run_patcher.start()
        self.run_mock.io_bound = AsyncMock()
        self.addCleanup(self.run_patcher.stop)

        self.config_mock = config_module_mock.config_manager
        self.config_mock.get_language.return_value = 'EN'
        self.config_mock.get_bulk_add_page_size.return_value = 50

        with patch.object(bulk_add_module, 'SingleCardView'), \
             patch.object(bulk_add_module, 'StructureDeckDialog'), \
             patch.object(bulk_add_module, 'FilterPane'):
            self.page = BulkAddPage()
            self.page.current_collection_obj = MagicMock()
            self.page.state['selected_collection'] = 'TestCol'

    async def test_update_condition(self):
        # Setup
        self.page.state['update_apply_cond'] = True
        self.page.state['default_condition'] = 'Played'
        self.page.state['default_language'] = 'EN'
        self.page.state['default_first_ed'] = False

        # Input Entry
        api_card = MagicMock()
        api_card.id = 123
        api_card.name = "Test Card"

        entry = BulkCollectionEntry(
            id="test_id",
            api_card=api_card,
            quantity=3,
            set_code="LOB-EN001",
            set_name="LOB",
            rarity="Ultra Rare",
            language="EN",
            condition="Near Mint",
            first_edition=False,
            image_url="url",
            image_id=123,
            variant_id="var_123",
            price=10.0
        )

        # Act
        await self.page.process_batch_update([entry])

        # Assert
        # Check CollectionEditor calls
        # 1. Remove old (NM)
        # 2. Add new (Played)

        self.assertEqual(self.collection_editor_mock.apply_change.call_count, 2)

        # Call 1: Remove Old
        call1 = self.collection_editor_mock.apply_change.call_args_list[0]
        self.assertEqual(call1.kwargs['quantity'], -3)
        self.assertEqual(call1.kwargs['condition'], 'Near Mint')

        # Call 2: Add New
        call2 = self.collection_editor_mock.apply_change.call_args_list[1]
        self.assertEqual(call2.kwargs['quantity'], 3)
        self.assertEqual(call2.kwargs['condition'], 'Played')

        # Check Changelog
        self.changelog_manager_mock.log_batch_change.assert_called_once()

    async def test_update_mixed(self):
        # Update Lang and Cond
        self.page.state['update_apply_lang'] = True
        self.page.state['update_apply_cond'] = True
        self.page.state['default_language'] = 'DE'
        self.page.state['default_condition'] = 'Poor'

        # Input: EN, NM
        api_card = MagicMock()
        entry = BulkCollectionEntry(
            id="test_id",
            api_card=api_card,
            quantity=1,
            set_code="LOB-EN001",
            set_name="LOB",
            rarity="UR",
            language="EN",
            condition="Near Mint",
            first_edition=False,
            image_url="url",
            image_id=123,
            variant_id="var_123",
            price=0.0
        )

        await self.page.process_batch_update([entry])

        print("Calls:", self.collection_editor_mock.apply_change.call_args_list)

        # Verify Add New has DE and Poor
        call2 = self.collection_editor_mock.apply_change.call_args_list[1]
        self.assertEqual(call2.kwargs['language'], 'DE')
        self.assertEqual(call2.kwargs['condition'], 'Poor')

    async def test_no_update_needed(self):
        # Update Cond to NM, but card is already NM
        self.page.state['update_apply_cond'] = True
        self.page.state['default_condition'] = 'Near Mint'

        api_card = MagicMock()
        entry = BulkCollectionEntry(
            id="test_id",
            api_card=api_card,
            quantity=1,
            set_code="LOB-EN001",
            set_name="LOB",
            rarity="UR",
            language="EN",
            condition="Near Mint",
            first_edition=False,
            image_url="url",
            image_id=123,
            variant_id="var_123",
            price=0.0
        )

        await self.page.process_batch_update([entry])

        self.collection_editor_mock.apply_change.assert_not_called()

if __name__ == '__main__':
    unittest.main()
