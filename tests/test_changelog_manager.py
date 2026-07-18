from types import SimpleNamespace

from src.core.changelog_manager import ChangelogManager


def test_log_ids_use_timestamps_without_scanning_existing_lines(tmp_path, monkeypatch):
    manager = ChangelogManager(str(tmp_path))
    timestamps = iter([1_000_000_001, 1_000_000_002])
    monkeypatch.setattr(
        "src.core.changelog_manager.time",
        SimpleNamespace(time_ns=lambda: next(timestamps)),
    )

    manager.log_change("cards.json", "ADD", {"card_id": 1}, 1)
    manager.log_change("cards.json", "REMOVE", {"card_id": 1}, 1)

    history = manager.load_history("cards.json")
    assert [entry["id"] for entry in history] == [1_000_000_001, 1_000_000_002]
    assert [entry["timestamp"] for entry in history] == [1.000000001, 1.000000002]
