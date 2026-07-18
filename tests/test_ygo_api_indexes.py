from src.core.models import ApiCard
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
