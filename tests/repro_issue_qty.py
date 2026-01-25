import pytest
from unittest.mock import AsyncMock, Mock, patch
from src.ui.components.single_card_view import SingleCardView
from src.core.models import ApiCard, ApiCardImage, ApiCardSet, Collection, CollectionCard, CollectionVariant, CollectionEntry

@pytest.mark.asyncio
async def test_collectors_view_non_english_qty():
    # Setup
    view = SingleCardView()

    # API Data
    card_set_en = ApiCardSet(set_name="Test Set", set_code="TEST-EN001", set_rarity="Common", set_price="1.00", variant_id="v_en")

    api_card = ApiCard(
        id=1, name="Test Card", type="Monster", frameType="normal", desc="Desc",
        card_images=[ApiCardImage(id=1, image_url="u", image_url_small="s")],
        card_sets=[card_set_en]
    )

    # Collection Data - User owns German version
    # "TEST-DE001" is the German equivalent of "TEST-EN001"
    # User owns 3 copies.

    col_entry = CollectionEntry(language="DE", condition="Near Mint", first_edition=False, quantity=3, storage_location="Box 1")
    col_variant = CollectionVariant(
        variant_id="v_de", # Different ID? Or same? Usually different if code differs.
        set_code="TEST-DE001",
        rarity="Common",
        image_id=1,
        entries=[col_entry]
    )
    col_card = CollectionCard(card_id=1, name="Test Card", variants=[col_variant])
    collection = Collection(name="Test Col", cards=[col_card], storage_definitions=[])

    save_callback = AsyncMock()

    with patch('nicegui.ui.dialog'), \
         patch('nicegui.ui.card'), \
         patch('nicegui.ui.button'), \
         patch('nicegui.ui.row'), \
         patch('nicegui.ui.column'), \
         patch('nicegui.ui.image'), \
         patch('nicegui.ui.label') as mock_label, \
         patch('nicegui.ui.separator'), \
         patch('nicegui.ui.grid'), \
         patch('nicegui.ui.markdown'), \
         patch('nicegui.ui.chip'), \
         patch('nicegui.ui.expansion'), \
         patch('nicegui.ui.select'), \
         patch('nicegui.ui.checkbox'), \
         patch('nicegui.ui.number'), \
         patch('src.ui.components.single_card_view.image_manager.image_exists', return_value=False):

        # Simulate opening the view for the German card
        # owned_count=3, set_code="TEST-DE001", language="DE"
        await view.open_collectors(
            card=api_card,
            owned_count=3,
            set_code="TEST-DE001",
            rarity="Common",
            set_name="Test Set",
            language="DE",
            condition="Near Mint",
            first_edition=False,
            image_id=1,
            current_collection=collection,
            save_callback=save_callback
        )

        # Verify that "Total Owned" label was updated with "3"
        # The label is updated in update_display_stats -> owned_label.text = str(cur_owned)
        # We need to capture the instance of label used for owned count.
        # Since we mocked ui.label, we iterate calls.

        found_qty = False
        for call in mock_label.call_args_list:
            # We are looking for a call where text="3"
            if call.args and str(call.args[0]) == "3":
                found_qty = True
                break
            # Or text might be set via property later

        # Actually, update_display_stats sets .text property.
        # The mock return value's .text attribute is what we check.
        # But ui.label() returns a new mock each time.
        # We need to capture the specific label instance created for "Total Owned".

        # Let's inspect the logic in SingleCardView to see if we can trigger the issue.
        # If the issue exists, cur_owned will be 0.

        # Re-verify logic manually here:
        # 1. initial_base_code: "TEST-DE001" is not in options (only TEST-EN001).
        #    transform_set_code("TEST-EN001", "DE") -> "TEST-DE001". Match!
        #    initial_base_code = "TEST-EN001".
        # 2. input_state = { ..., set_base_code="TEST-EN001", language="DE" }
        # 3. update_display_stats():
        #    final_code = transform("TEST-EN001", "DE") -> "TEST-DE001".
        #    Iterate collection:
        #      v.set_code is "TEST-DE001". Match!
        #      e.language is "DE". Match!
        #      qty += 3.
        # It SHOULD work.

        # What if e.language is "de" (lowercase) in DB?
        col_entry.language = "de" # Try reproducing case sensitive issue

        await view.open_collectors(
            card=api_card,
            owned_count=3,
            set_code="TEST-DE001",
            rarity="Common",
            set_name="Test Set",
            language="DE",
            condition="Near Mint",
            first_edition=False,
            image_id=1,
            current_collection=collection, # Passed with lowercase 'de' entry
            save_callback=save_callback
        )

        # If case sensitivity is the issue, this should result in 0 found (if logic is strict).
