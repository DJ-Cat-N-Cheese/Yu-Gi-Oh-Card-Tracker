import asyncio
import os
from typing import Any, Callable, Dict, List, Optional, TypeVar

from fastapi import APIRouter, HTTPException, Query, status
from nicegui import run

from src.api.models import (
    CardAddRequest,
    CardSetQuantityRequest,
    CardsListResponse,
    CollectionCreateRequest,
    CollectionListResponse,
    ImportResponse,
    ImportUrlRequest,
    MessageResponse,
    MutationResponse,
    SetDetailResponse,
)
from src.core.changelog_manager import changelog_manager
from src.core.models import ApiCard, Collection, CollectionCard
from src.core.persistence import persistence
from src.services.collection_editor import CollectionEditor
from src.services.ygo_api import ygo_service
from src.services.yugipedia_service import yugipedia_service

router = APIRouter(prefix="/api/v1", tags=["api"])

T = TypeVar("T")


async def _io_bound(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    try:
        return await run.io_bound(func, *args, **kwargs)
    except RuntimeError:
        return await asyncio.to_thread(func, *args, **kwargs)


def _safe_filename(filename: str) -> str:
    safe_name = os.path.basename(filename)
    if safe_name != filename or not safe_name.endswith((".json", ".yaml", ".yml")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid collection filename")
    return safe_name


def _filename_for_collection_name(name: str) -> str:
    filename = name if name.endswith((".json", ".yaml", ".yml")) else f"{name}.json"
    return _safe_filename(filename)


async def _load_collection(filename: str) -> Collection:
    safe_name = _safe_filename(filename)
    try:
        return await _io_bound(persistence.load_collection, safe_name)
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found") from None
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


async def _save_collection(collection: Collection, filename: str) -> None:
    await _io_bound(persistence.save_collection, collection, _safe_filename(filename))


async def _resolve_api_card(card_id: int) -> ApiCard:
    cards = await ygo_service.load_card_database()
    api_card = next((card for card in cards if card.id == card_id), None)
    if api_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found in database")
    return api_card


def _find_collection_card(collection: Collection, card_id: int) -> CollectionCard:
    collection_card = next((card for card in collection.cards if card.card_id == card_id), None)
    if collection_card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card not found in collection")
    return collection_card


def _matches(value: Optional[str], expected: Optional[str]) -> bool:
    return expected is None or value == expected


def _mutation_card_data(
    request: CardAddRequest | CardSetQuantityRequest,
    api_card: ApiCard,
) -> Dict[str, Any]:
    return {
        "card_id": request.card_id,
        "name": api_card.name,
        "set_code": request.set_code,
        "rarity": request.rarity,
        "language": request.language,
        "condition": request.condition,
        "first_edition": request.first_edition,
        "storage_location": request.storage_location,
        "image_id": request.image_id,
        "variant_id": request.variant_id,
    }


async def _apply_and_persist(
    filename: str,
    collection: Collection,
    api_card: ApiCard,
    request: CardAddRequest | CardSetQuantityRequest,
    mode: str,
    action: str,
) -> MutationResponse:
    modified = CollectionEditor.apply_change(
        collection=collection,
        api_card=api_card,
        set_code=request.set_code,
        rarity=request.rarity,
        language=request.language,
        quantity=request.quantity,
        condition=request.condition,
        first_edition=request.first_edition,
        image_id=request.image_id,
        variant_id=request.variant_id,
        mode=mode,
        storage_location=request.storage_location,
    )
    if not modified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Collection was not changed")

    await _save_collection(collection, filename)
    await _io_bound(
        changelog_manager.log_change,
        _safe_filename(filename),
        action,
        _mutation_card_data(request, api_card),
        request.quantity,
    )
    return MutationResponse(modified=True, collection=collection)


@router.get("/collections", response_model=CollectionListResponse)
async def list_collections() -> CollectionListResponse:
    collections = await _io_bound(persistence.list_collections)
    return CollectionListResponse(collections=collections)


@router.get("/collections/{filename}", response_model=Collection)
async def get_collection(filename: str) -> Collection:
    return await _load_collection(filename)


@router.post("/collections", response_model=Collection, status_code=status.HTTP_201_CREATED)
async def create_collection(request: CollectionCreateRequest) -> Collection:
    filename = _filename_for_collection_name(request.name)
    existing = await _io_bound(persistence.list_collections)
    if filename in existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Collection already exists")

    collection = Collection(name=request.name.removesuffix(".json").removesuffix(".yaml").removesuffix(".yml"))
    await _save_collection(collection, filename)
    return collection


@router.delete("/collections/{filename}", response_model=MessageResponse)
async def delete_collection(filename: str) -> MessageResponse:
    safe_name = _safe_filename(filename)
    filepath = os.path.join(persistence.data_dir, safe_name)
    if not await _io_bound(os.path.exists, filepath):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Collection not found")
    await _io_bound(os.remove, filepath)
    return MessageResponse(message="Collection deleted")


@router.get("/collections/{filename}/cards", response_model=CardsListResponse)
async def list_collection_cards(
    filename: str,
    card_id: Optional[int] = None,
    name: Optional[str] = None,
    archetype: Optional[str] = None,
) -> CardsListResponse:
    collection = await _load_collection(filename)
    cards = collection.cards
    if card_id is not None:
        cards = [card for card in cards if card.card_id == card_id]
    if name:
        lowered_name = name.lower()
        cards = [card for card in cards if lowered_name in card.name.lower()]
    if archetype:
        database_cards = await ygo_service.load_card_database()
        matching_ids = {
            card.id
            for card in database_cards
            if card.archetype and archetype.lower() in card.archetype.lower()
        }
        cards = [card for card in cards if card.card_id in matching_ids]
    return CardsListResponse(cards=cards)


@router.get("/collections/{filename}/cards/{card_id}", response_model=CollectionCard)
async def get_collection_card(filename: str, card_id: int) -> CollectionCard:
    collection = await _load_collection(filename)
    return _find_collection_card(collection, card_id)


@router.post("/collections/{filename}/cards", response_model=MutationResponse, status_code=status.HTTP_201_CREATED)
async def add_collection_card(filename: str, request: CardAddRequest) -> MutationResponse:
    collection = await _load_collection(filename)
    api_card = await _resolve_api_card(request.card_id)
    return await _apply_and_persist(filename, collection, api_card, request, mode="ADD", action="ADD")


@router.patch("/collections/{filename}/cards/{card_id}", response_model=MutationResponse)
async def set_collection_card_quantity(
    filename: str,
    card_id: int,
    request: CardSetQuantityRequest,
) -> MutationResponse:
    if request.card_id != card_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Path card_id and body card_id differ")
    collection = await _load_collection(filename)
    api_card = await _resolve_api_card(card_id)
    return await _apply_and_persist(filename, collection, api_card, request, mode="SET", action="SET")


@router.delete("/collections/{filename}/cards/{card_id}", response_model=MutationResponse)
async def delete_collection_card(
    filename: str,
    card_id: int,
    variant_id: Optional[str] = None,
    set_code: Optional[str] = None,
    rarity: Optional[str] = None,
    language: Optional[str] = None,
    condition: Optional[str] = None,
    first_edition: Optional[bool] = None,
    storage_location: Optional[str] = None,
) -> MutationResponse:
    collection = await _load_collection(filename)
    collection_card = _find_collection_card(collection, card_id)
    api_card = await _resolve_api_card(card_id)

    removals: List[CardSetQuantityRequest] = []
    for variant in list(collection_card.variants):
        if variant_id and variant.variant_id != variant_id:
            continue
        if not _matches(variant.set_code, set_code) or not _matches(variant.rarity, rarity):
            continue
        for entry in list(variant.entries):
            if not _matches(entry.language, language):
                continue
            if not _matches(entry.condition, condition):
                continue
            if first_edition is not None and entry.first_edition != first_edition:
                continue
            if not _matches(entry.storage_location, storage_location):
                continue
            removals.append(
                CardSetQuantityRequest(
                    card_id=card_id,
                    set_code=variant.set_code,
                    rarity=variant.rarity,
                    quantity=0,
                    language=entry.language,
                    condition=entry.condition,
                    first_edition=entry.first_edition,
                    storage_location=entry.storage_location,
                    image_id=variant.image_id,
                    variant_id=variant.variant_id,
                )
            )

    if not removals:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matching card entry not found")

    modified = False
    for removal in removals:
        modified = CollectionEditor.apply_change(
            collection=collection,
            api_card=api_card,
            set_code=removal.set_code,
            rarity=removal.rarity,
            language=removal.language,
            quantity=0,
            condition=removal.condition,
            first_edition=removal.first_edition,
            image_id=removal.image_id,
            variant_id=removal.variant_id,
            mode="SET",
            storage_location=removal.storage_location,
        ) or modified

    if not modified:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Collection was not changed")

    await _save_collection(collection, filename)
    for removal in removals:
        await _io_bound(
            changelog_manager.log_change,
            _safe_filename(filename),
            "REMOVE",
            _mutation_card_data(removal, api_card),
            0,
        )
    return MutationResponse(modified=True, collection=collection)


@router.get("/db/cards", response_model=List[ApiCard])
async def search_card_database(
    name: Optional[str] = None,
    archetype: Optional[str] = None,
    type: Optional[str] = None,
    attribute: Optional[str] = None,
    race: Optional[str] = None,
    frameType: Optional[str] = None,
) -> List[ApiCard]:
    cards = await ygo_service.load_card_database()

    def contains(value: Optional[str], expected: Optional[str]) -> bool:
        return expected is None or bool(value and expected.lower() in value.lower())

    return [
        card
        for card in cards
        if contains(card.name, name)
        and contains(card.archetype, archetype)
        and contains(card.type, type)
        and contains(card.attribute, attribute)
        and contains(card.race, race)
        and contains(card.frameType, frameType)
    ]


@router.get("/db/cards/{card_id}", response_model=ApiCard)
async def get_database_card(card_id: int) -> ApiCard:
    return await _resolve_api_card(card_id)


@router.get("/db/sets", response_model=List[Dict[str, Any]])
async def list_sets() -> List[Dict[str, Any]]:
    return await ygo_service.get_all_sets_info()


@router.get("/db/sets/{set_code}", response_model=SetDetailResponse)
async def get_set(set_code: str) -> SetDetailResponse:
    set_info = await ygo_service.get_set_info(set_code)
    if set_info is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set not found")
    cards = await ygo_service.get_set_cards(set_code)
    return SetDetailResponse(set=set_info, cards=cards)


@router.post("/db/import/set", response_model=ImportResponse)
async def import_set_from_yugipedia(request: ImportUrlRequest) -> ImportResponse:
    set_data = await yugipedia_service.get_set_details(request.url)
    if not set_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Set details not found")
    success, message = await ygo_service.import_set_from_yugipedia(set_data)
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return ImportResponse(success=success, message=message)


@router.post("/db/import/card", response_model=ImportResponse)
async def import_card_from_yugipedia(request: ImportUrlRequest) -> ImportResponse:
    card_data = await yugipedia_service.get_card_details(request.url)
    if not card_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Card details not found")
    success, message = await ygo_service.import_from_yugipedia(card_data, card_data.get("sets", []))
    if not success:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return ImportResponse(success=success, message=message)


@router.get("/collections/{filename}/changelog", response_model=List[Dict[str, Any]])
async def get_collection_changelog(filename: str, limit: Optional[int] = Query(None, ge=1)) -> List[Dict[str, Any]]:
    _safe_filename(filename)
    history = await _io_bound(changelog_manager.load_history, filename)
    if limit is not None:
        return history[-limit:]
    return history
