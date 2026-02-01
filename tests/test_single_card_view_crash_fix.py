import pytest
from unittest.mock import MagicMock, patch
import sys
import importlib

class TestSingleCardViewCrashFix:
    def test_render_inventory_management_missing_image_id(self):
        """
        Regression test: Ensure that opening a card with a custom image_id that is NOT
        in the official art options does not cause a crash (ValueError in ui.select).
        """
        # Prepare Mocks
        mock_ui = MagicMock()
        mock_run = MagicMock()
        mock_nicegui = MagicMock()
        mock_nicegui.ui = mock_ui
        mock_nicegui.run = mock_run

        # Patch sys.modules to mock nicegui during the import of the component
        with patch.dict(sys.modules, {'nicegui': mock_nicegui, 'nicegui.ui': mock_ui, 'nicegui.run': mock_run}):
            # We must ensure the module is (re)loaded with the mocks in place
            # If it was already loaded by another test, we need to reload it.
            # If not, we import it.
            module_name = 'src.ui.components.single_card_view'
            if module_name in sys.modules:
                del sys.modules[module_name]

            import src.ui.components.single_card_view
            importlib.reload(src.ui.components.single_card_view)
            from src.ui.components.single_card_view import SingleCardView
            from src.services.ygo_api import ApiCard

            view = SingleCardView()

            # Mock inputs
            card = MagicMock(spec=ApiCard)
            card.id = 12345
            # Setup card images
            img1 = MagicMock()
            img1.id = 11111
            img1.image_url = "http://example.com/1.jpg"
            img2 = MagicMock()
            img2.id = 22222
            img2.image_url = "http://example.com/2.jpg"
            card.card_images = [img1, img2]

            # Scenario: User has a custom art ID 99999 assigned, which is NOT in card.card_images
            input_state = {
                'set_base_code': 'TEST-EN001',
                'rarity': 'Common',
                'image_id': 99999, # The custom ID
                'language': 'EN',
                'condition': 'Near Mint',
                'first_edition': False,
                'quantity': 1,
                'storage_location': None
            }

            set_options = {'TEST-EN001': 'Test Set'}
            set_info_map = {}

            # Mock UI context managers
            mock_ui.card.return_value.__enter__.return_value = MagicMock()
            mock_ui.grid.return_value.__enter__.return_value = MagicMock()
            mock_ui.row.return_value.__enter__.return_value = MagicMock()

            # Reset mocks to clear any calls during import or init
            mock_ui.select.reset_mock()

            # Call the method
            view._render_inventory_management(
                card=card,
                input_state=input_state,
                set_options=set_options,
                set_info_map=set_info_map,
                on_change_callback=MagicMock(),
                on_save_callback=MagicMock()
            )

            # Find the call to ui.select for 'Artwork'
            artwork_select_call = None
            for call in mock_ui.select.call_args_list:
                args, kwargs = call
                if kwargs.get('label') == 'Artwork':
                    artwork_select_call = call
                    break

            assert artwork_select_call is not None, "Artwork select component was not rendered"

            # Verify options
            args, kwargs = artwork_select_call
            options = args[0] if args else kwargs.get('options')

            # Check if the custom ID is in the options keys
            assert 99999 in options, f"Custom image ID 99999 was not added to artwork options: {options.keys()}"
            assert options[99999] == "Custom/Unknown (ID: 99999)"
