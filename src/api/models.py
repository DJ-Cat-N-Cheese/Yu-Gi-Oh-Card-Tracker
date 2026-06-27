from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from src.core.models import Collection, CollectionCard


class CollectionCreateRequest(BaseModel):
    name: str = Field(..., min_length=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        name = value.strip()
        if not name:
            raise ValueError("name must not be empty")
        return name


class CardMutationRequest(BaseModel):
    card_id: int
    set_code: str = Field(..., min_length=1)
    rarity: str = Field(..., min_length=1)
    quantity: int = Field(..., ge=0)
    language: str = "EN"
    condition: str = "Near Mint"
    first_edition: bool = False
    storage_location: Optional[str] = None
    image_id: Optional[int] = None
    variant_id: Optional[str] = None


class CardAddRequest(CardMutationRequest):
    quantity: int = Field(..., gt=0)


class CardSetQuantityRequest(CardMutationRequest):
    pass


class ImportUrlRequest(BaseModel):
    url: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    message: str


class MutationResponse(BaseModel):
    modified: bool
    collection: Collection


class CollectionListResponse(BaseModel):
    collections: List[str]


class CardsListResponse(BaseModel):
    cards: List[CollectionCard]


class SetDetailResponse(BaseModel):
    set: Dict[str, Any]
    cards: List[Any]


class ImportResponse(BaseModel):
    success: bool
    message: str


ChangeAction = Literal["ADD", "REMOVE", "SET"]
