from nicegui import app, ui

from src.services.auth_service import AUTH_REVISION_KEY, AUTH_SESSION_KEY
from src.ui.theme import apply_theme

NAV_ITEMS = [
    ('Dashboard', '/'),
    ('Collection', '/collection'),
    ('Storage', '/storage'),
    ('Browse Sets', '/sets'),
    ('Deck Builder', '/decks'),
    ('Bulk Add', '/bulk_add'),
    ('Scan Cards', '/scan'),
    ('Import Tools', '/import'),
    ('Edit Card DB', '/db_editor'),
]


def create_layout(content_function):
    """Wrap a protected page in the standard navigation and header."""
    apply_theme()

    try:
        current_path = ui.context.client.page.path
    except (AttributeError, RuntimeError):
        current_path = ''

    def logout() -> None:
        app.storage.user.pop(AUTH_SESSION_KEY, None)
        app.storage.user.pop(AUTH_REVISION_KEY, None)
        ui.navigate.to('/login')

    def nav_row(text: str, target: str | None = None, on_click=None, active: bool = False):
        row = ui.element('div').classes('oy-navrow w-full' + (' active' if active else ''))
        if on_click is None and target is not None:
            on_click = lambda target=target: ui.navigate.to(target)  # noqa: E731
        if on_click is not None:
            row.on('click', on_click)
        with row:
            if active:
                ui.element('span').classes('oy-dot')
            ui.label(text)
        return row

    with ui.left_drawer(value=True, bordered=False).props(
        'breakpoint=1023 :width="234" show-if-above'
    ) as left_drawer:
        with ui.column().classes('h-full w-full gap-6 px-2 py-5'):
            ui.label('OpenYuGi').classes('oy-logo px-3')

            with ui.column().classes('w-full gap-0.5'):
                ui.label('NAVIGATION').classes('oy-navlabel mb-1')
                for text, target in NAV_ITEMS:
                    nav_row(text, target, active=current_path == target)

            with ui.column().classes('w-full gap-0.5 mt-auto pt-4 border-t border-white/10'):
                ui.label('SETTINGS').classes('oy-navlabel mb-1')
                nav_row('Configuration', '/settings', active=current_path == '/settings')
                nav_row('Log out', on_click=logout)

    # Floating drawer toggle for small screens (no top bar on desktop)
    ui.button(icon='menu', on_click=left_drawer.toggle).props('flat round').classes(
        'lg:hidden fixed top-2 left-2 z-50 bg-black/40 text-white'
    )

    with ui.column().classes('w-full items-start px-4 py-5 lg:px-8 lg:py-7'):
        content_function()
