from dataclasses import dataclass
from src.services.ygo_api import ApiCard

@dataclass
class LibraryEntry:
    id: str # Unique ID for UI (card_id + variant hash)
    api_card: ApiCard
    set_code: str
    set_name: str
    rarity: str
    image_url: str
    image_id: int
    price: float = 0.0

@dataclass
class BulkCollectionEntry:
    id: str # Unique ID for UI
    api_card: ApiCard
    quantity: int
    set_code: str
    set_name: str
    rarity: str
    language: str
    condition: str
    first_edition: bool
    image_url: str
    image_id: int
    variant_id: str
    price: float = 0.0
