import sys
from unittest.mock import MagicMock, AsyncMock, patch
import unittest
from tests.mock_imports import import_with_module_mocks

# Setup mocks for dependencies FIRST
persistence_mock = MagicMock()
persistence_mock.load_ui_state.return_value = {}
persistence_mock.list_collections.return_value = []
persistence_module_mock = MagicMock()
persistence_module_mock.persistence = persistence_mock

changelog_manager_mock = MagicMock()
changelog_module_mock = MagicMock()
changelog_module_mock.changelog_manager = changelog_manager_mock

config_manager_mock = MagicMock()
config_manager_mock.get_language.return_value = 'EN'
config_manager_mock.get_bulk_add_page_size.return_value = 50
config_module_mock = MagicMock()
config_module_mock.config_manager = config_manager_mock

ygo_service_mock = MagicMock()
# Important: ensure_card_variant must be AsyncMock
ygo_service_mock.ensure_card_variant = AsyncMock(return_value=True)
ygo_service_mock.ensure_card_variants = AsyncMock(return_value=1)
ygo_api_module_mock = MagicMock()
ygo_api_module_mock.ygo_service = ygo_service_mock
ygo_api_module_mock.ApiCard = MagicMock

image_manager_mock = MagicMock()
image_manager_module_mock = MagicMock()
image_manager_module_mock.image_manager = image_manager_mock

collection_editor_mock = MagicMock()
collection_editor_mock.CollectionEditor.apply_change.return_value = True
collection_editor_module_mock = MagicMock()
collection_editor_module_mock.CollectionEditor = collection_editor_mock.CollectionEditor

# Now mock nicegui
run_mock = MagicMock()
async def async_return(*args, **kwargs):
    return MagicMock()
run_mock.io_bound = AsyncMock(side_effect=async_return)

ui_mock = MagicMock()
ui_mock.notify = MagicMock()

nicegui_mock = MagicMock()
nicegui_mock.run = run_mock
nicegui_mock.ui = ui_mock

# Import the class under test
bulk_add_module = import_with_module_mocks(
    'src.ui.bulk_add',
    {
        'src.core.persistence': persistence_module_mock,
        'src.core.changelog_manager': changelog_module_mock,
        'src.core.config': config_module_mock,
        'src.services.ygo_api': ygo_api_module_mock,
        'src.services.image_manager': image_manager_module_mock,
        'src.services.collection_editor': collection_editor_module_mock,
        'nicegui': nicegui_mock,
        'nicegui.ui': ui_mock,
        'nicegui.run': run_mock,
    },
)
BulkAddPage = bulk_add_module.BulkAddPage

class TestBulkAddUpdate(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        with patch.object(bulk_add_module, 'SingleCardView'), \
             patch.object(bulk_add_module, 'StructureDeckDialog'), \
             patch.object(bulk_add_module, 'FilterPane'):
            self.page = BulkAddPage()
            self.page.current_collection_obj = MagicMock()
            self.page.state['selected_collection'] = "TestCol.json"
            # Reset mock calls
            ygo_service_mock.ensure_card_variant.reset_mock()
            ygo_service_mock.ensure_card_variants.reset_mock()

    async def test_update_collection_calls_ensure_variant(self):
        api_card = MagicMock()
        api_card.id = 123

        await self.page._update_collection(
            api_card=api_card,
            set_code="LOB-DE001",
            rarity="Ultra Rare",
            lang="DE",
            qty=1,
            cond="Near Mint",
            first=False,
            img_id=456,
            mode='ADD'
        )

        ygo_service_mock.ensure_card_variant.assert_awaited_once()
        args, kwargs = ygo_service_mock.ensure_card_variant.call_args
        self.assertEqual(kwargs['card_id'], 123)
        self.assertEqual(kwargs['set_code'], "LOB-DE001")
        self.assertEqual(kwargs['language'], "en") # Config returns EN lower

    async def test_process_batch_add_calls_ensure_variants(self):
        # Setup entries
        api_card = MagicMock()
        api_card.id = 123

        # Entry mimicking LibraryEntry
        entry = MagicMock()
        entry.api_card = api_card
        entry.set_code = "LOB-EN001"
        entry.rarity = "Ultra Rare"
        entry.image_id = 456

        # Set default language to DE to force transformation
        self.page.state['default_language'] = 'DE'

        # We need to mock transform_set_code since it's imported in bulk_add
        with patch.object(bulk_add_module, 'transform_set_code', return_value="LOB-DE001"):
            await self.page.process_batch_add([entry])

        ygo_service_mock.ensure_card_variants.assert_awaited_once()
        args, kwargs = ygo_service_mock.ensure_card_variants.call_args
        self.assertEqual(len(args[0]), 1)
        self.assertEqual(args[0][0]['set_code'], "LOB-DE001")

if __name__ == '__main__':
    unittest.main()
