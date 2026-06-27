from typing import Any

import pytest
from fastapi.testclient import TestClient

import main
from src.api import routes
from src.core.models import ApiCard, ApiCardImage, ApiCardSet, Collection
from src.core.persistence import PersistenceManager


@pytest.fixture
def api_client(tmp_path, monkeypatch):
    collections_dir = tmp_path / "collections"
    changelogs_dir = tmp_path / "changelogs"
    collections_dir.mkdir()
    changelogs_dir.mkdir()

    test_persistence = PersistenceManager(data_dir=str(collections_dir), decks_dir=str(tmp_path / "decks"))
    monkeypatch.setattr(routes, "persistence", test_persistence)
    monkeypatch.setattr(routes.changelog_manager, "data_dir", str(changelogs_dir))

    async def immediate_io_bound(func: Any, *args: Any, **kwargs: Any):
        return func(*args, **kwargs)

    monkeypatch.setattr(routes.run, "io_bound", immediate_io_bound)

    card = ApiCard(
        id=1,
        name="Blue-Eyes White Dragon",
        type="Normal Monster",
        frameType="normal",
        desc="Legendary dragon.",
        race="Dragon",
        attribute="LIGHT",
        archetype="Blue-Eyes",
        card_images=[
            ApiCardImage(
                id=1,
                image_url="https://example.test/card.jpg",
                image_url_small="https://example.test/card-small.jpg",
            )
        ],
        card_sets=[
            ApiCardSet(
                set_name="Legend of Blue Eyes White Dragon",
                set_code="LOB-001",
                set_rarity="Ultra Rare",
                card_image_id=1,
            )
        ],
    )

    async def load_card_database(language: str = "en"):
        return [card]

    monkeypatch.setattr(routes.ygo_service, "load_card_database", load_card_database)
    return TestClient(main.app)


def test_list_collections(api_client):
    routes.persistence.save_collection(Collection(name="Test"), "test.json")

    response = api_client.get("/api/v1/collections")

    assert response.status_code == 200
    assert response.json() == {"collections": ["test.json"]}


def test_get_collection(api_client):
    routes.persistence.save_collection(Collection(name="Test"), "test.json")

    response = api_client.get("/api/v1/collections/test.json")

    assert response.status_code == 200
    assert response.json()["name"] == "Test"
    assert response.json()["cards"] == []


def test_add_card(api_client):
    routes.persistence.save_collection(Collection(name="Test"), "test.json")

    response = api_client.post(
        "/api/v1/collections/test.json/cards",
        json={
            "card_id": 1,
            "set_code": "LOB-001",
            "rarity": "Ultra Rare",
            "quantity": 2,
            "language": "EN",
            "condition": "Near Mint",
            "first_edition": True,
            "storage_location": "Binder A",
            "image_id": 1,
        },
    )

    assert response.status_code == 201
    collection = response.json()["collection"]
    assert collection["cards"][0]["card_id"] == 1
    assert collection["cards"][0]["variants"][0]["entries"][0]["quantity"] == 2


def test_set_quantity(api_client):
    routes.persistence.save_collection(Collection(name="Test"), "test.json")
    api_client.post(
        "/api/v1/collections/test.json/cards",
        json={
            "card_id": 1,
            "set_code": "LOB-001",
            "rarity": "Ultra Rare",
            "quantity": 2,
            "language": "EN",
            "condition": "Near Mint",
            "first_edition": False,
            "image_id": 1,
        },
    )

    response = api_client.patch(
        "/api/v1/collections/test.json/cards/1",
        json={
            "card_id": 1,
            "set_code": "LOB-001",
            "rarity": "Ultra Rare",
            "quantity": 5,
            "language": "EN",
            "condition": "Near Mint",
            "first_edition": False,
            "image_id": 1,
        },
    )

    assert response.status_code == 200
    assert response.json()["collection"]["cards"][0]["variants"][0]["entries"][0]["quantity"] == 5


def test_delete_card(api_client):
    routes.persistence.save_collection(Collection(name="Test"), "test.json")
    api_client.post(
        "/api/v1/collections/test.json/cards",
        json={
            "card_id": 1,
            "set_code": "LOB-001",
            "rarity": "Ultra Rare",
            "quantity": 1,
            "language": "EN",
            "condition": "Near Mint",
            "first_edition": False,
            "image_id": 1,
        },
    )

    response = api_client.delete("/api/v1/collections/test.json/cards/1")

    assert response.status_code == 200
    assert response.json()["collection"]["cards"] == []


def test_search_card_db(api_client):
    response = api_client.get("/api/v1/db/cards", params={"name": "blue-eyes", "race": "dragon"})

    assert response.status_code == 200
    assert response.json()[0]["id"] == 1


def test_import_card_from_yugipedia(api_client, monkeypatch):
    async def get_card_details(url: str):
        return {"name": "Imported Card", "sets": [{"set_code": "IMP-001"}]}

    async def import_from_yugipedia(card_data, selected_sets, language: str = "en"):
        assert selected_sets == [{"set_code": "IMP-001"}]
        return True, "Imported card"

    monkeypatch.setattr(routes.yugipedia_service, "get_card_details", get_card_details)
    monkeypatch.setattr(routes.ygo_service, "import_from_yugipedia", import_from_yugipedia)

    response = api_client.post("/api/v1/db/import/card", json={"url": "https://yugipedia.test/card"})

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Imported card"}


def test_import_set_from_yugipedia(api_client, monkeypatch):
    async def get_set_details(url: str):
        return {"name": "Imported Set", "code": "IMP", "cards": [{"name": "Imported Card"}]}

    async def import_set_from_yugipedia(set_data, language: str = "en"):
        assert set_data["code"] == "IMP"
        return True, "Imported set"

    monkeypatch.setattr(routes.yugipedia_service, "get_set_details", get_set_details)
    monkeypatch.setattr(routes.ygo_service, "import_set_from_yugipedia", import_set_from_yugipedia)

    response = api_client.post("/api/v1/db/import/set", json={"url": "https://yugipedia.test/set"})

    assert response.status_code == 200
    assert response.json() == {"success": True, "message": "Imported set"}
