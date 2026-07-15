from nicegui import app, ui

from src.services.auth_service import AUTH_REVISION_KEY, AUTH_SESSION_KEY
from src.ui.theme import apply_theme


def create_layout(content_function):
    """Wrap a protected page in the standard navigation and header."""
    apply_theme()

    def logout() -> None:
        app.storage.user.pop(AUTH_SESSION_KEY, None)
        app.storage.user.pop(AUTH_REVISION_KEY, None)
        ui.navigate.to('/login')

    with ui.left_drawer(value=True).classes('bg-dark text-white') as left_drawer:
        with ui.column().classes('w-full q-mt-md'):
            ui.label('Navigation').classes('text-grey-4 q-px-md text-sm uppercase font-bold')

            def nav_button(text, icon, target):
                ui.button(text, icon=icon, on_click=lambda: ui.navigate.to(target)).props(
                    'flat align=left'
                ).classes('w-full text-grey-3 hover:bg-white/10')

            nav_button('Dashboard', 'dashboard', '/')
            nav_button('Collection', 'style', '/collection')
            nav_button('Storage', 'inventory_2', '/storage')
            nav_button('Browse Sets', 'library_books', '/sets')
            nav_button('Deck Builder', 'construction', '/decks')
            nav_button('Bulk Add', 'playlist_add', '/bulk_add')
            nav_button('Scan Cards', 'camera', '/scan')
            nav_button('Import Tools', 'qr_code_scanner', '/import')
            nav_button('Edit Card DB', 'edit', '/db_editor')

            ui.separator().classes('q-my-md bg-grey-8')
            ui.label('Account').classes('text-grey-4 q-px-md text-sm uppercase font-bold')
            nav_button('Settings', 'settings', '/settings')
            ui.button('Log out', icon='logout', on_click=logout).props(
                'flat align=left'
            ).classes('w-full text-grey-3 hover:bg-white/10')

    with ui.header().classes(replace='row items-center').classes('bg-primary text-white'):
        ui.button(on_click=lambda: left_drawer.toggle(), icon='menu').props('flat color=white')
        ui.label('OpenYuGi').classes('text-h6 q-ml-md font-bold')

    with ui.column().classes('w-full q-pa-md items-start'):
        content_function()
