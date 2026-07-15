import asyncio

from nicegui import app, run, ui

from src.services.auth_service import AUTH_REVISION_KEY, AUTH_SESSION_KEY, auth_service
from src.ui.theme import apply_theme


def session_is_authenticated() -> bool:
    return bool(
        app.storage.user.get(AUTH_SESSION_KEY)
        and app.storage.user.get(AUTH_REVISION_KEY) == auth_service.revision()
    )


def _safe_next_path(next_path: str | None) -> str:
    """Return a local navigation target, falling back to the dashboard."""
    if isinstance(next_path, str) and next_path.startswith('/') and not next_path.startswith('//'):
        return next_path
    return '/'


def login_page(next_path: str | None = None) -> None:
    """Render the only page available without an authenticated session."""
    apply_theme()
    destination = _safe_next_path(next_path)
    if session_is_authenticated():
        ui.navigate.to(destination)
        return

    async def login() -> None:
        submit.props('loading disable')
        try:
            authenticated = await run.io_bound(auth_service.authenticate, username.value, password.value)
            if authenticated:
                app.storage.user.clear()
                app.storage.user[AUTH_SESSION_KEY] = True
                app.storage.user[AUTH_REVISION_KEY] = auth_service.revision()
                ui.navigate.to(destination)
                return

            # A fixed delay makes online guessing slower without blocking NiceGUI's event loop.
            await asyncio.sleep(1)
            password.set_value('')
            ui.notify('Invalid username or password.', type='negative')
        finally:
            submit.props(remove='loading disable')

    with ui.column().classes('absolute-center items-center w-full q-px-md'):
        with ui.card().classes('w-full max-w-md q-pa-lg shadow-12'):
            ui.label('OpenYuGi').classes('text-h4 text-weight-bold text-center w-full')
            ui.label('Sign in to manage your collection').classes(
                'text-subtitle1 text-grey-5 text-center w-full q-mb-md'
            )
            username = ui.input('Username', value='').props(
                'outlined autocomplete=username autofocus'
            ).classes('w-full')
            password = ui.input('Password', password=True, password_toggle_button=True).props(
                'outlined autocomplete=current-password'
            ).classes('w-full')
            password.on('keydown.enter', login)
            submit = ui.button('Sign in', icon='login', on_click=login).props(
                'color=secondary size=lg'
            ).classes('w-full q-mt-md')
