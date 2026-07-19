import re
from unittest.mock import MagicMock, call, patch

from src.ui.layout import NAV_ITEMS
from src.ui import theme


def test_chart_palette_and_metric_classes_are_valid_and_shared():
    assert len(theme.CHART_COLORS) == 10
    assert all(re.fullmatch(r'#[0-9a-fA-F]{6}', color) for color in theme.CHART_COLORS)
    assert theme.METRIC_VALUE_CLASSES == {
        'primary': 'text-white',
        'secondary': 'oy-text-accent',
        'accent': 'oy-text-blue',
        'info': 'oy-text-blue',
        'positive': 'oy-text-green',
    }


def test_global_css_is_offline_and_remaps_legacy_gray_text():
    assert 'fonts.googleapis.com' not in theme.GLOBAL_CSS
    assert 'fonts.gstatic.com' not in theme.GLOBAL_CSS
    assert '.text-gray-300' in theme.GLOBAL_CSS
    assert '.text-gray-600' in theme.GLOBAL_CSS


def test_apply_theme_uses_distinct_semantic_colors_and_enables_dark_mode():
    dark_mode = MagicMock()
    with patch.object(theme.ui, 'colors') as colors, \
         patch.object(theme.ui, 'dark_mode', return_value=dark_mode), \
         patch.object(theme.ui, 'add_head_html') as add_head_html:
        theme.apply_theme()

    palette = colors.call_args.kwargs
    assert palette['primary'] == '#1e1e2e'
    assert palette['secondary'] == '#cba6f7'
    assert palette['primary'] != palette['secondary']
    dark_mode.enable.assert_called_once_with()
    add_head_html.assert_not_called()


def test_global_styles_are_registered_as_shared_head_content():
    with patch.object(theme.ui, 'add_head_html') as add_head_html:
        theme.install_global_styles()

    add_head_html.assert_called_once_with(theme.GLOBAL_CSS, shared=True)


def test_page_header_builds_title_and_optional_subtitle():
    header = MagicMock()
    column = MagicMock()
    column.classes.return_value = header
    title_label = MagicMock()
    subtitle_label = MagicMock()

    with patch.object(theme.ui, 'column', return_value=column), \
         patch.object(theme.ui, 'label', side_effect=[title_label, subtitle_label]) as label:
        result = theme.page_header('Collection', 'Browse every card.')

    assert result is header
    label.assert_has_calls([call('Collection'), call('Browse every card.')])
    title_label.classes.assert_called_once_with('oy-h1')
    subtitle_label.classes.assert_called_once_with('oy-sub')


def test_navigation_covers_every_protected_route():
    nav_routes = {route for _, route in NAV_ITEMS}
    assert nav_routes | {'/settings'} == {
        '/', '/collection', '/storage', '/sets', '/decks', '/bulk_add',
        '/scan', '/import', '/db_editor', '/settings',
    }
