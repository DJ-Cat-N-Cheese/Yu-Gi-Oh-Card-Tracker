import asyncio
import hmac
import uuid
from urllib.parse import urlencode

from nicegui import app, run, ui

from src.services.auth_service import AUTH_REVISION_KEY, AUTH_SESSION_KEY, auth_service
from src.ui.theme import apply_theme

TEMP_AUTH_TOKEN_KEY = 'temp_auth_token'


def session_is_authenticated() -> bool:
    return bool(
        app.storage.user.get(AUTH_SESSION_KEY)
        and app.storage.user.get(AUTH_REVISION_KEY) == auth_service.revision()
    )


def _safe_next_path(next_path: str | None) -> str:
    """Return a local navigation target, falling back to the dashboard."""
    if not isinstance(next_path, str):
        return '/'

    # Browsers ignore these characters while resolving URLs. Remove them before
    # checking for protocol-relative paths so '/\t\\example.com' cannot become
    # '//example.com' in the browser.
    cleaned = ''.join(character for character in next_path if character not in '\t\r\n')
    if (
        cleaned.startswith('/')
        and not cleaned.startswith('//')
        and '\\' not in cleaned
    ):
        return cleaned
    return '/'


async def complete_login_callback(token: str | None, next_path: str | None) -> str | None:
    """Rotate the browser session after a login and return its safe destination.

    This runs from the callback page's HTTP request, where NiceGUI can still
    write the browser cookie. It must not be called from a WebSocket handler.
    """
    old_user_storage = app.storage.user
    expected_token = old_user_storage.get(TEMP_AUTH_TOKEN_KEY)
    if not (
        isinstance(token, str)
        and isinstance(expected_token, str)
        and hmac.compare_digest(token, expected_token)
    ):
        return None

    session_id = str(uuid.uuid4())
    app.storage.browser['id'] = session_id
    await app.storage._create_user_storage(session_id)  # pylint: disable=protected-access
    app.storage.user[AUTH_SESSION_KEY] = True
    app.storage.user[AUTH_REVISION_KEY] = auth_service.revision()
    old_user_storage.pop(TEMP_AUTH_TOKEN_KEY, None)
    return _safe_next_path(next_path)


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
                token = str(uuid.uuid4())
                app.storage.user[TEMP_AUTH_TOKEN_KEY] = token
                callback_query = urlencode({'token': token, 'next': destination})
                ui.navigate.to(f'/login/callback?{callback_query}')
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
