import asyncio
import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
from tests.mock_imports import import_with_module_mocks

# Mock nicegui
mock_ui = MagicMock()
mock_run = MagicMock()

# Mock dependencies before importing BulkAddPage
persistence_module_mock = MagicMock()
changelog_module_mock = MagicMock()
config_module_mock = MagicMock()
ygo_api_module_mock = MagicMock()
image_manager_module_mock = MagicMock()
collection_editor_module_mock = MagicMock()

from src.core.models import ApiCard, ApiCardSet, Collection, CollectionCard, CollectionVariant, CollectionEntry
bulk_add_module = import_with_module_mocks(
    'src.ui.bulk_add',
    {
        'nicegui': mock_ui,
        'nicegui.ui': mock_ui,
        'nicegui.run': mock_run,
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

class TestBulkAddFiltering(unittest.TestCase):
    def setUp(self):
        # Setup mocks
        self.persistence_mock = persistence_module_mock.persistence
        self.persistence_mock.list_collections.return_value = []
        self.persistence_mock.load_ui_state.return_value = {}

        self.config_mock = config_module_mock.config_manager
        self.config_mock.get_language.return_value = 'en'
        self.config_mock.get_bulk_add_page_size.return_value = 50

        # Initialize page
        with patch.object(bulk_add_module, 'SingleCardView'), \
             patch.object(bulk_add_module, 'StructureDeckDialog'), \
             patch.object(bulk_add_module, 'FilterPane'):
            self.page = BulkAddPage()

        # Mock render methods
        self.page.render_collection_content = MagicMock()
        self.page.render_collection_content.refresh = MagicMock()
        self.page.collection_filter_pane = MagicMock()

    def test_filter_set_by_name(self):
        # Setup data
        c1 = ApiCard(id=1, name="Blue-Eyes", type="Monster", frameType="normal", desc="desc")

        entry1 = BulkCollectionEntry(
            id="1", api_card=c1, quantity=1, set_code="LOB-EN001", set_name="Legend of Blue Eyes White Dragon",
            rarity="Ultra Rare", language="EN", condition="Near Mint", first_edition=False,
            image_url="", image_id=1, variant_id="v1"
        )

        self.page.col_state['collection_cards'] = [entry1]
        self.page.col_state['collection_page_size'] = 50

        # Test Filter by Set Name (partial match)
        self.page.col_state['filter_set'] = "Legend of Blue Eyes | LOB"

        asyncio.run(self.page.apply_collection_filters())

        res = self.page.col_state['collection_filtered']
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].id, "1")

    def test_load_collection_data_populates_set_name(self):
        # Mock API Card
        c1 = ApiCard(id=1, name="Blue-Eyes", type="Monster", frameType="normal", desc="desc")
        c1.card_sets = [
            ApiCardSet(set_name="Legend of Blue Eyes White Dragon", set_code="LOB-EN001", set_rarity="Ultra Rare"),
            ApiCardSet(set_name="Structure Deck: Kaiba", set_code="SDK-001", set_rarity="Ultra Rare")
        ]

        # Mock api_card_map
        self.page.api_card_map = {1: c1}

        # Mock Collection Data
        col = Collection(name="Test Col", cards=[
            CollectionCard(card_id=1, name="Blue-Eyes", variants=[
                CollectionVariant(variant_id="v1", set_code="LOB-EN001", rarity="Ultra Rare", entries=[
                    CollectionEntry(quantity=1)
                ])
            ])
        ])

        # Setup run.io_bound to return the collection
        # We patch the 'io_bound' method on the 'run' object in src.ui.bulk_add
        with patch.object(bulk_add_module.run, 'io_bound', new_callable=AsyncMock) as mock_io:
            async def io_bound_side_effect(func, *args, **kwargs):
                return func(*args, **kwargs)
            mock_io.side_effect = io_bound_side_effect

            self.page.state['selected_collection'] = "Test Col"
            self.persistence_mock.load_collection.return_value = col

            # Run load_collection_data
            asyncio.run(self.page.load_collection_data())

            # Verify
            entries = self.page.col_state['collection_cards']
            self.assertEqual(len(entries), 1)
            entry = entries[0]
            self.assertEqual(entry.set_code, "LOB-EN001")
            self.assertEqual(entry.set_name, "Legend of Blue Eyes White Dragon")

            # Test Unknown Set Logic
            col2 = Collection(name="Test Col 2", cards=[
                CollectionCard(card_id=1, name="Blue-Eyes", variants=[
                    CollectionVariant(variant_id="v2", set_code="UNKNOWN-CODE", rarity="Common", entries=[
                        CollectionEntry(quantity=1)
                    ])
                ])
            ])
            self.persistence_mock.load_collection.return_value = col2
            asyncio.run(self.page.load_collection_data())

            entries = self.page.col_state['collection_cards']
            entry = entries[0]
            self.assertEqual(entry.set_name, "Unknown Set")

if __name__ == '__main__':
    unittest.main()
