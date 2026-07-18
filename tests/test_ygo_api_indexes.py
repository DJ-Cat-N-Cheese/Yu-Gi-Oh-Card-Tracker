import asyncio

from src.core.models import ApiCard, ApiCardSet
from src.services.ygo_api import YugiohService


def _card(card_id: int, name: str) -> ApiCard:
    return ApiCard(id=card_id, name=name, type="Spell Card", frameType="spell", desc="")


def test_card_lookups_use_indexes_rebuilt_from_cache():
    service = YugiohService()
    dark_hole = _card(53129443, "Dark Hole")
    service._cards_cache["en"] = [dark_hole]

    assert service.get_card(53129443) is dark_hole
    assert service.search_by_name("DARK HOLE") is dark_hole
    assert service._cards_by_id["en"] == {53129443: dark_hole}
    assert service._cards_by_name["en"] == {"dark hole": dark_hole}


def test_rebuild_card_lookups_replaces_stale_entries():
    service = YugiohService()
    service._rebuild_card_lookups("en", [_card(1, "Old Card")])
    replacement = _card(2, "New Card")

    service._rebuild_card_lookups("en", [replacement])

    assert service.get_card(1) is None
    assert service.search_by_name("Old Card") is None
    assert service.get_card(2) is replacement


def test_card_lookups_preserve_first_duplicate_card():
    service = YugiohService()
    first = _card(1, "Duplicate")
    duplicate_id = _card(1, "Different Name")
    duplicate_name = _card(2, "Duplicate")

    service._rebuild_card_lookups("en", [first, duplicate_id, duplicate_name])

    assert service.get_card(1) is first
    assert service.search_by_name("duplicate") is first


def test_set_card_counts_are_cached_and_deduplicate_variants():
    service = YugiohService()
    card = _card(1, "Card With Reprints")
    card.card_sets = [
        ApiCardSet(set_name="Legend", set_code="LOB-EN001", set_rarity="Rare"),
        ApiCardSet(set_name="Legend", set_code="LOB-DE001", set_rarity="Common"),
        ApiCardSet(set_name="Starter", set_code="SDK-001", set_rarity="Common"),
    ]
    service._cards_cache["en"] = [card]

    first_result = asyncio.run(service.get_real_set_counts())
    card.card_sets.clear()
    second_result = asyncio.run(service.get_real_set_counts())

    assert first_result == {"LOB": 1, "SDK": 1}
    assert second_result is first_result


def test_filter_metadata_is_compiled_with_set_counts():
    service = YugiohService()
    card = ApiCard(
        id=1,
        name="Dark Magician",
        type="Normal Monster",
        frameType="normal",
        desc="",
        race="Spellcaster",
        archetype="Dark Magician",
        card_sets=[ApiCardSet(set_name="Legend", set_code="LOB-EN005", set_rarity="Ultra Rare")],
    )
    service._cards_cache["en"] = [card]

    metadata = asyncio.run(service.get_filter_metadata())

    assert metadata["available_sets"] == ["Legend | LOB"]
    assert metadata["available_monster_races"] == ["Spellcaster"]
    assert metadata["available_st_races"] == []
    assert metadata["available_archetypes"] == ["Dark Magician"]
