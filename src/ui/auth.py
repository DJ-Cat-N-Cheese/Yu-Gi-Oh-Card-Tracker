import asyncio
import hmac
import logging
import time
import uuid
from urllib.parse import urlencode

from nicegui import app, run, ui

from src.services.auth_service import AUTH_REVISION_KEY, AUTH_SESSION_KEY, auth_service
from src.ui.theme import apply_theme

TEMP_AUTH_TOKEN_KEY = 'temp_auth_token'
TEMP_AUTH_TOKEN_EXPIRY_KEY = 'temp_auth_token_expiry'
TEMP_AUTH_TOKEN_TTL_SECONDS = 60

logger = logging.getLogger(__name__)


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
    storage = app.storage
    old_user_storage = storage.user
    expected_token = old_user_storage.get(TEMP_AUTH_TOKEN_KEY)
    expires_at = old_user_storage.get(TEMP_AUTH_TOKEN_EXPIRY_KEY)
    if not (
        isinstance(token, str)
        and isinstance(expected_token, str)
        and hmac.compare_digest(token, expected_token)
        and isinstance(expires_at, (int, float))
        and time.time() <= expires_at
    ):
        if isinstance(token, str) and expected_token is None:
            logger.warning('Rejected replayed or consumed login callback token.')
        elif isinstance(expires_at, (int, float)) and time.time() > expires_at:
            logger.warning('Rejected expired login callback token.')
            old_user_storage.pop(TEMP_AUTH_TOKEN_KEY, None)
            old_user_storage.pop(TEMP_AUTH_TOKEN_EXPIRY_KEY, None)
        return None

    # Consume the token before the first await so a callback URL is single-use.
    old_user_storage.pop(TEMP_AUTH_TOKEN_KEY, None)
    old_user_storage.pop(TEMP_AUTH_TOKEN_EXPIRY_KEY, None)
    old_session_id = storage.browser.get('id')
    session_id = str(uuid.uuid4())
    storage.browser['id'] = session_id
    await storage._create_user_storage(session_id)  # pylint: disable=protected-access
    storage.user[AUTH_SESSION_KEY] = True
    storage.user[AUTH_REVISION_KEY] = auth_service.revision()

    # NiceGUI retains per-user storage by session ID. Clear its persistent data
    # and remove the old in-memory entry once the replacement session is ready.
    old_user_storage.clear()
    users = getattr(storage, '_users', None)
    if isinstance(users, dict) and old_session_id is not None:
        users.pop(old_session_id, None)
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
                app.storage.user[TEMP_AUTH_TOKEN_EXPIRY_KEY] = time.time() + TEMP_AUTH_TOKEN_TTL_SECONDS
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
        with ui.card().classes('w-full max-w-md q-pa-lg gap-1'):
            ui.label('OpenYuGi').classes('oy-logo text-[26px] text-center w-full')
            ui.label('Sign in to manage your collection').classes(
                'oy-sub text-center w-full q-mb-md'
            )
            username = ui.input('Username', value='').props(
                'outlined autocomplete=username autofocus'
            ).classes('w-full')
            password = ui.input('Password', password=True, password_toggle_button=True).props(
                'outlined autocomplete=current-password'
            ).classes('w-full')
            password.on('keydown.enter', login)
            submit = ui.button('Sign in', icon='login', on_click=login).props(
                'color=secondary size=lg rounded unelevated'
            ).classes('w-full q-mt-md')
