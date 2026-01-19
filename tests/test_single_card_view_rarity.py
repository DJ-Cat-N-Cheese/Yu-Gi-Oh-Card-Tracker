import unittest
from unittest.mock import MagicMock, patch, AsyncMock
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.ui.components.single_card_view import SingleCardView, STANDARD_RARITIES
from src.services.ygo_api import ApiCard, ApiCardSet

class TestSingleCardViewRarity(unittest.IsolatedAsyncioTestCase):
    async def test_rarity_dropdown_updates_on_set_change(self):
        with patch('src.ui.components.single_card_view.ui') as mock_ui:
            # Reset mocks (patch creates a new one)

            # Setup Mock UI Context Managers
            mock_context = MagicMock()
            mock_context.__enter__.return_value = mock_context
            mock_context.__exit__.return_value = None

            mock_ui.card.return_value = mock_context
            mock_ui.row.return_value = mock_context
            mock_ui.column.return_value = mock_context
            mock_ui.dialog.return_value = mock_context
            mock_ui.expansion.return_value = mock_context

            # Capture select components
            selects = []
            def mock_select(options, label='', value=None, on_change=None):
                sel = MagicMock()
                # Important: Chained methods must return self
                sel.classes.return_value = sel
                sel.props.return_value = sel

                sel.options = options
                sel.value = value
                sel.label = label
                sel.on_change = on_change

                # Mock on_value_change (used for set_select)
                def on_value_change(callback):
                    # We store the callback so we can trigger it manually
                    sel.on_change_handler = callback
                sel.on_value_change = on_value_change

                selects.append(sel)
                return sel
            mock_ui.select.side_effect = mock_select

            # Instantiate View
            view = SingleCardView()

            # Dummy Data
            card = MagicMock(spec=ApiCard)
            card.id = 123
            card.card_sets = [
                ApiCardSet(set_name="Set A", set_code="SETA-001", set_rarity="Ultra Rare"),
                ApiCardSet(set_name="Set A", set_code="SETA-001", set_rarity="Secret Rare"),
                ApiCardSet(set_name="Set B", set_code="SETB-001", set_rarity="Common"),
            ]
            card.card_images = []

            # Prepare Inputs
            input_state = {
                'language': 'EN',
                'set_base_code': 'SETA-001',
                'rarity': 'Ultra Rare',
                'condition': 'Near Mint',
                'first_edition': False,
                'image_id': 123,
                'quantity': 1
            }

            set_options = {'SETA-001': 'Set A (SETA-001)', 'SETB-001': 'Set B (SETB-001)'}
            set_info_map = {
                'SETA-001': card.card_sets[0],
                'SETB-001': card.card_sets[2]
            }

            # The Rarity Map we EXPECT to pass after refactoring
            rarity_map = {
                'SETA-001': {'Ultra Rare', 'Secret Rare'},
                'SETB-001': {'Common'}
            }

            on_save_callback = AsyncMock()

            # --- EXECUTE ---
            view._render_inventory_management(
                card=card,
                input_state=input_state,
                set_options=set_options,
                set_info_map=set_info_map,
                on_change_callback=MagicMock(),
                on_save_callback=on_save_callback,
                default_set_base_code='SETA-001',
                rarity_map=rarity_map # New Argument
            )

            # Find Selects
            # Since ui.select is called multiple times, we need to find the right ones.
            # set_select label='Set Name'
            # rarity_select label='Rarity'

            set_select = next((s for s in selects if s.label == 'Set Name'), None)
            rarity_select = next((s for s in selects if s.label == 'Rarity'), None)

            self.assertIsNotNone(set_select, "Set Name select not found")
            self.assertIsNotNone(rarity_select, "Rarity select not found")

            # ASSERTION 1: Initial Rarity Options for SETA-001
            expected_set_a_rarities = {'Ultra Rare', 'Secret Rare'}
            current_options_set = set(rarity_select.options)

            self.assertTrue(expected_set_a_rarities.issubset(current_options_set), f"Initial options missing expected rarities: {current_options_set}")

            # ASSERTION 2: Change to SETB-001
            # Simulate Set Change
            new_set_event = MagicMock()
            new_set_event.value = 'SETB-001'

            # Trigger the handler registered via on_value_change
            if hasattr(set_select, 'on_change_handler'):
                 set_select.on_change_handler(new_set_event)
            else:
                 self.fail("Set select handler not registered")

            # Check Rarity Options Update
            expected_set_b_rarities = {'Common'}
            current_options_set_b = set(rarity_select.options)

            self.assertEqual(current_options_set_b, expected_set_b_rarities, f"Expected only Common, got {current_options_set_b}")

if __name__ == '__main__':
    unittest.main()
