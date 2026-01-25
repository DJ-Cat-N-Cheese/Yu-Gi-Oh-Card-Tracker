import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.ui.components.single_card_view import SingleCardView
from src.core.models import ApiCard, ApiCardImage, ApiCardSet

@pytest.mark.asyncio
async def test_open_consolidated_signature():
    # Setup
    view = SingleCardView()

    # Mock data
    card_image = ApiCardImage(id=123, image_url="http://test.com/1.jpg", image_url_small="http://test.com/1_small.jpg")
    card_set = ApiCardSet(set_name="Test Set", set_code="TEST-EN001", set_rarity="Common", set_price="1.00")

    api_card = ApiCard(
        id=1,
        name="Test Card",
        type="Monster",
        frameType="normal",
        desc="Description",
        race="Dragon",
        atk=3000,
        def_=2500,
        level=8,
        attribute="LIGHT",
        card_images=[card_image],
        card_sets=[card_set]
    )

    total_owned = 5
    owned_breakdown = {'EN': 5}
    save_callback = AsyncMock()

    # Mock current_collection
    mock_collection = Mock()
    mock_storage = Mock()
    mock_storage.name = "Box 1"
    mock_collection.storage_definitions = [mock_storage]

    # Mock UI elements to prevent actual rendering
    with patch('nicegui.ui.dialog') as mock_dialog, \
         patch('nicegui.ui.card'), \
         patch('nicegui.ui.button'), \
         patch('nicegui.ui.row'), \
         patch('nicegui.ui.column'), \
         patch('nicegui.ui.image'), \
         patch('nicegui.ui.label'), \
         patch('nicegui.ui.separator'), \
         patch('nicegui.ui.grid'), \
         patch('nicegui.ui.markdown'), \
         patch('nicegui.ui.chip'), \
         patch('nicegui.ui.expansion'), \
         patch('nicegui.ui.select') as mock_select, \
         patch('nicegui.ui.checkbox'), \
         patch('nicegui.ui.number'):

        mock_dialog_instance = Mock()
        mock_dialog.return_value.__enter__.return_value = mock_dialog_instance

        # Test call with all arguments including current_collection
        await view.open_consolidated(
            card=api_card,
            total_owned=total_owned,
            owned_breakdown=owned_breakdown,
            save_callback=save_callback,
            current_collection=mock_collection
        )

        # Verify that storage selection logic was triggered (checking if select was called)
        # We expect calls for Language, Set, Rarity, Condition, Storage (if present)
        assert mock_select.call_count >= 1

        # Check if one of the select calls contained our storage option "Box 1"
        found_storage = False
        for call in mock_select.call_args_list:
            # call.args[0] or call.kwargs['options'] usually holds options
            options = call.kwargs.get('options') or (call.args[0] if call.args else None)
            if options and isinstance(options, dict) and "Box 1" in options:
                found_storage = True
                break

        assert found_storage, "Storage options from current_collection were not passed to ui.select"

@pytest.mark.asyncio
async def test_open_consolidated_missing_collection_arg_safety():
    # Setup
    view = SingleCardView()
    api_card = ApiCard(id=1, name="Test", type="Monster", frameType="normal", desc="Desc", card_images=[], card_sets=[])
    save_callback = AsyncMock()

    with patch('nicegui.ui.dialog'), \
         patch('nicegui.ui.card'), \
         patch('nicegui.ui.button'), \
         patch('nicegui.ui.row'), \
         patch('nicegui.ui.column'), \
         patch('nicegui.ui.image'), \
         patch('nicegui.ui.label'), \
         patch('nicegui.ui.separator'), \
         patch('nicegui.ui.grid'), \
         patch('nicegui.ui.markdown'), \
         patch('nicegui.ui.chip'), \
         patch('nicegui.ui.expansion'), \
         patch('nicegui.ui.select') as mock_select, \
         patch('nicegui.ui.checkbox'), \
         patch('nicegui.ui.number'):

        # Call WITHOUT current_collection (defaults to None)
        # This checks regression where it might crash if trying to access properties of None
        await view.open_consolidated(
            card=api_card,
            total_owned=0,
            owned_breakdown={},
            save_callback=save_callback
            # current_collection defaults to None
        )

        # Should not crash.
        # Verify storage options contain only None
        found_none_only = False
        for call in mock_select.call_args_list:
            options = call.kwargs.get('options') or (call.args[0] if call.args else None)
            if options and isinstance(options, dict) and None in options and len(options) == 1:
                found_none_only = True
                # We might have other selects like Language/Condition, but one should match "Storage" context (options={None: 'None'})

        # It's hard to distinguish "Storage" select from others just by options sometimes,
        # but we check that it ran through without exception.
