from unittest.mock import MagicMock, patch

from src.ui.components.single_card_view import SingleCardView


def test_close_button_uses_visible_glyph_without_icon_font():
    dialog = MagicMock()
    button = MagicMock()
    button.props.return_value = button
    button.classes.return_value = button

    with patch('src.ui.components.single_card_view.ui.button', return_value=button) as ui_button:
        result = SingleCardView._render_close_button(dialog)

    ui_button.assert_called_once_with('×', on_click=dialog.close)
    button.props.assert_called_once_with('flat round aria-label="Close" title="Close"')
    button.classes.assert_called_once_with(
        'oy-single-card-close absolute top-3 right-3 z-50'
    )
    assert result is button
