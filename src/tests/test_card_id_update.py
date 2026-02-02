import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import sys

# Mock nicegui.run since it's used in ygo_api
with patch.dict(sys.modules, {'nicegui': MagicMock(), 'nicegui.run': MagicMock()}):
    from src.services.ygo_api import YugiohService
    from src.core.models import ApiCard, ApiCardSet

@pytest.mark.asyncio
async def test_update_card_id():
    service = YugiohService()

    # Mock data
    original_id = 123
    new_id = 456

    variant_id = "v1"

    card = ApiCard(
        id=original_id,
        name="Test Card",
        type="Monster",
        frameType="normal",
        desc="Description",
        card_sets=[
            ApiCardSet(
                variant_id=variant_id,
                set_name="Test Set",
                set_code="TEST-EN001",
                set_rarity="Common",
                image_id=original_id
            )
        ],
        card_images=[]
    )

    # Test 1: Collision
    # Existing card with new_id
    existing_card = ApiCard(id=new_id, name="Collision", type="x", frameType="x", desc="x")
    service.load_card_database = AsyncMock(return_value=[card, existing_card])
    service.save_card_database = AsyncMock()

    result = await service.update_card_id(original_id, new_id)
    assert result is False

    # Test 2: Success
    service.load_card_database = AsyncMock(return_value=[card])
    service.save_card_database = AsyncMock()

    result = await service.update_card_id(original_id, new_id)

    assert result is True
    assert card.id == new_id
    # Check that variant ID has been updated
    assert card.card_sets[0].variant_id != variant_id

    service.save_card_database.assert_called_once()
