import unittest
from src.core.models import Collection, CollectionCard, CollectionVariant, CollectionEntry, ApiCard, ApiCardImage
from src.services.collection_editor import CollectionEditor

class MockApiCard(ApiCard):
    def __init__(self, id, name):
        super().__init__(
            id=id,
            name=name,
            type="Monster",
            frameType="normal",
            desc="Test Card",
            card_images=[ApiCardImage(id=id, image_url="url", image_url_small="small_url")]
        )

class TestCollectionMerge(unittest.TestCase):
    def setUp(self):
        # Create Collection A
        self.coll_a = Collection(name="Collection A")
        self.card1 = MockApiCard(1001, "Dark Magician")
        self.card2 = MockApiCard(1002, "Blue-Eyes White Dragon")

        # Add 1 Dark Magician to A
        CollectionEditor.apply_change(
            self.coll_a, self.card1, set_code="SDY-006", rarity="Ultra Rare",
            language="EN", quantity=1, condition="Near Mint", first_edition=True, mode='ADD'
        )

        # Add 1 Blue-Eyes to A
        CollectionEditor.apply_change(
            self.coll_a, self.card2, set_code="LOB-001", rarity="Ultra Rare",
            language="EN", quantity=1, condition="Near Mint", first_edition=True, mode='ADD'
        )

        # Create Collection B
        self.coll_b = Collection(name="Collection B")

        # Add 2 Dark Magician to B (Same variant/printing)
        CollectionEditor.apply_change(
            self.coll_b, self.card1, set_code="SDY-006", rarity="Ultra Rare",
            language="EN", quantity=2, condition="Near Mint", first_edition=True, mode='ADD'
        )

        # Add 1 Dark Magician to B (Different condition)
        CollectionEditor.apply_change(
            self.coll_b, self.card1, set_code="SDY-006", rarity="Ultra Rare",
            language="EN", quantity=1, condition="Played", first_edition=True, mode='ADD'
        )

    def test_merge_logic(self):
        # Create New Collection
        new_coll = Collection(name="Merged Collection")

        # Merge A into New
        for card in self.coll_a.cards:
            api_card = MockApiCard(card.card_id, card.name) # Simulate lookup
            for variant in card.variants:
                for entry in variant.entries:
                    CollectionEditor.apply_change(
                        new_coll, api_card,
                        set_code=variant.set_code,
                        rarity=variant.rarity,
                        language=entry.language,
                        quantity=entry.quantity,
                        condition=entry.condition,
                        first_edition=entry.first_edition,
                        image_id=variant.image_id,
                        mode='ADD'
                    )

        # Merge B into New
        for card in self.coll_b.cards:
            api_card = MockApiCard(card.card_id, card.name) # Simulate lookup
            for variant in card.variants:
                for entry in variant.entries:
                    CollectionEditor.apply_change(
                        new_coll, api_card,
                        set_code=variant.set_code,
                        rarity=variant.rarity,
                        language=entry.language,
                        quantity=entry.quantity,
                        condition=entry.condition,
                        first_edition=entry.first_edition,
                        image_id=variant.image_id,
                        mode='ADD'
                    )

        # Assertions

        # Check Dark Magician (SDY-006, NM, 1st) -> 1 (from A) + 2 (from B) = 3
        dm_card = next((c for c in new_coll.cards if c.card_id == 1001), None)
        self.assertIsNotNone(dm_card)
        dm_nm_entry = None
        for v in dm_card.variants:
            for e in v.entries:
                if e.condition == "Near Mint":
                    dm_nm_entry = e

        self.assertIsNotNone(dm_nm_entry)
        self.assertEqual(dm_nm_entry.quantity, 3)

        # Check Dark Magician (Played) -> 1
        dm_played_entry = None
        for v in dm_card.variants:
            for e in v.entries:
                if e.condition == "Played":
                    dm_played_entry = e
        self.assertIsNotNone(dm_played_entry)
        self.assertEqual(dm_played_entry.quantity, 1)

        # Check Blue-Eyes -> 1
        be_card = next((c for c in new_coll.cards if c.card_id == 1002), None)
        self.assertIsNotNone(be_card)
        self.assertEqual(be_card.total_quantity, 1)

        # Verify Originals Unchanged
        self.assertEqual(self.coll_a.total_cards, 2)
        self.assertEqual(self.coll_b.total_cards, 3)

if __name__ == '__main__':
    unittest.main()
