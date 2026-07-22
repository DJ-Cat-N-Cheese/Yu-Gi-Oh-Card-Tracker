import asyncio
import unittest
from unittest.mock import MagicMock, patch
from src.core.models import ApiCard
from tests.mock_imports import import_with_module_mocks

# --- Mocks Setup ---

# 1. NiceGUI
mock_ui = MagicMock()
mock_run = MagicMock()

# 2. Persistence
mock_persistence_module = MagicMock()
mock_persistence_obj = MagicMock()
mock_persistence_obj.load_ui_state.return_value = {}
mock_persistence_module.persistence = mock_persistence_obj

# 3. Other Services
ygo_api_mock = MagicMock()
image_manager_mock = MagicMock()
config_mock = MagicMock()

# 5. FilterPane (used in db_editor)
filter_pane_mock = MagicMock()

# 6. SingleCardView (used in db_editor)
mock_single_card_view = MagicMock()
# It also imports STANDARD_RARITIES
mock_single_card_view.STANDARD_RARITIES = ["Common", "Rare"]

# --- Imports after Mocks ---
db_editor_module = import_with_module_mocks(
    'src.ui.db_editor',
    {
        'nicegui': mock_ui,
        'nicegui.ui': mock_ui,
        'nicegui.run': mock_run,
        'src.core.persistence': mock_persistence_module,
        'src.services.ygo_api': ygo_api_mock,
        'src.services.image_manager': image_manager_mock,
        'src.core.config': config_mock,
        'src.ui.components.filter_pane': filter_pane_mock,
        'src.ui.components.single_card_view': mock_single_card_view,
    },
)
DbEditorPage = db_editor_module.DbEditorPage
DbEditorRow = db_editor_module.DbEditorRow

# Helpers
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super(AsyncMock, self).__call__(*args, **kwargs)

class TestDbEditorSort(unittest.TestCase):
    def setUp(self):
        # We need to patch 'run' where it is used in db_editor
        self.run_patcher = patch.object(db_editor_module, 'run')
        self.mock_run = self.run_patcher.start()

        # Configure io_bound to just return result
        async def side_effect(func, *args, **kwargs):
            return func(*args, **kwargs)

        self.mock_run.io_bound = AsyncMock(side_effect=side_effect)

        self.page = DbEditorPage()

        # Mock async methods to prevent actual execution logic
        self.page.prepare_current_page_images = AsyncMock()

        # Mock UI updates
        self.page.update_pagination = MagicMock()
        self.page.update_pagination_labels = MagicMock()

        self.page.render_card_display = MagicMock()
        self.page.render_card_display.refresh = MagicMock()

    def tearDown(self):
        self.run_patcher.stop()

    def test_sort_by_set_code(self):
        # Create test data
        c1 = ApiCard(id=1, name="Card A", type="Monster", frameType="normal", desc="")
        c2 = ApiCard(id=2, name="Card B", type="Monster", frameType="normal", desc="")
        c3 = ApiCard(id=3, name="Card C", type="Monster", frameType="normal", desc="")

        row1 = DbEditorRow(
            api_card=c1,
            set_code="LOB-002",
            set_name="Legend",
            rarity="Common",
            image_url="",
            image_id=None,
            variant_id="1"
        )
        row2 = DbEditorRow(
            api_card=c2,
            set_code="LOB-001",
            set_name="Legend",
            rarity="Common",
            image_url="",
            image_id=None,
            variant_id="2"
        )
        row3 = DbEditorRow(
            api_card=c3,
            set_code="NO SET",
            set_name="No Set",
            rarity="Common",
            image_url="",
            image_id=None,
            variant_id="3"
        )

        # Set initial state
        self.page.state['cards_rows'] = [row1, row2, row3]

        # --- TEST 1: Ascending ---
        self.page.state['sort_by'] = 'Set Code'
        self.page.state['sort_descending'] = False

        # Run filters
        asyncio.run(self.page.apply_filters())

        res = self.page.state['filtered_items']
        self.assertEqual(len(res), 3)
        self.assertEqual(res[0].set_code, "LOB-001")
        self.assertEqual(res[1].set_code, "LOB-002")
        self.assertEqual(res[2].set_code, "NO SET")

        # --- TEST 2: Descending ---
        self.page.state['sort_descending'] = True

        asyncio.run(self.page.apply_filters())

        res = self.page.state['filtered_items']
        self.assertEqual(res[0].set_code, "NO SET")
        self.assertEqual(res[1].set_code, "LOB-002")
        self.assertEqual(res[2].set_code, "LOB-001")

if __name__ == '__main__':
    unittest.main()
