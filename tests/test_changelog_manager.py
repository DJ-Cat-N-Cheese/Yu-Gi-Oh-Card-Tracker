from types import SimpleNamespace

from src.core.changelog_manager import ChangelogManager


def test_log_ids_are_unique_when_wall_clock_is_coarse(tmp_path, monkeypatch):
    manager = ChangelogManager(str(tmp_path))
    monkeypatch.setattr(
        "src.core.changelog_manager.time",
        SimpleNamespace(time_ns=lambda: 1_000_000_001),
    )

    manager.log_change("cards.json", "ADD", {"card_id": 1}, 1)
    manager.log_change("cards.json", "REMOVE", {"card_id": 1}, 1)

    history = manager.load_history("cards.json")
    assert len({entry["id"] for entry in history}) == 2
    assert [entry["timestamp"] for entry in history] == [1.000000001, 1.000000001]
