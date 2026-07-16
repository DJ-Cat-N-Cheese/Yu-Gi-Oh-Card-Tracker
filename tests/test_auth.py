import json
import logging
import os
import stat
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from nicegui.storage import set_storage_secret
from werkzeug.security import check_password_hash

import main
from src.core.config import ConfigManager
from src.services.auth_middleware import is_public_path
from src.services.auth_service import AuthService, get_storage_secret
from src.ui.auth import (
    AUTH_REVISION_KEY,
    AUTH_SESSION_KEY,
    TEMP_AUTH_TOKEN_KEY,
    TEMP_AUTH_TOKEN_EXPIRY_KEY,
    _safe_next_path,
    complete_login_callback,
)


@pytest.fixture
def auth(tmp_path):
    manager = ConfigManager(str(tmp_path / 'config.json'))
    return manager, AuthService(manager)


def test_default_credentials_are_hashed_and_authenticate(auth):
    manager, service = auth

    assert manager.get_auth_username() == 'admin'
    assert manager.get_auth_password_hash() != 'admin'
    assert manager.get_auth_password_hash().startswith('scrypt:')
    assert check_password_hash(manager.get_auth_password_hash(), 'admin')
    assert service.authenticate('admin', 'admin')
    assert not service.authenticate('admin', 'wrong')
    assert not service.authenticate('someone-else', 'admin')
    assert not service.authenticate('管理者', 'admin')

    persisted = json.loads(Path(manager.config_file).read_text(encoding='utf-8'))
    assert persisted['auth_password_hash'] != 'admin'
    assert 'auth_password' not in persisted
    assert stat.S_IMODE(Path(manager.config_file).stat().st_mode) == 0o600


def test_updating_credentials_requires_current_password_and_persists(auth):
    manager, service = auth
    original_revision = service.revision()

    with pytest.raises(ValueError, match='Current password is incorrect'):
        service.update_credentials('wrong', 'collector', 'secure-pass', 'secure-pass')

    service.update_credentials('admin', 'collector', 'secure-pass', 'secure-pass')

    reloaded = AuthService(ConfigManager(manager.config_file))
    assert not reloaded.authenticate('admin', 'admin')
    assert reloaded.authenticate('collector', 'secure-pass')
    assert reloaded.revision() != original_revision


@pytest.mark.parametrize(
    ('username', 'message'),
    [
        ('', 'Username is required'),
        ('x' * 65, '64 characters or fewer'),
        ('bad\nname', 'control characters'),
    ],
)
def test_username_validation(auth, username, message):
    _, service = auth
    with pytest.raises(ValueError, match=message):
        service.update_credentials('admin', username)


def test_password_validation_and_confirmation(auth):
    _, service = auth
    with pytest.raises(ValueError, match='do not match'):
        service.update_credentials('admin', 'admin', 'four', 'five')
    with pytest.raises(ValueError, match='at least 8'):
        service.update_credentials('admin', 'admin', '1234567', '1234567')
    with pytest.raises(ValueError, match='128 characters or fewer'):
        service.update_credentials('admin', 'admin', 'x' * 129, 'x' * 129)


def test_username_can_change_without_changing_password(auth):
    _, service = auth
    service.update_credentials('admin', 'new-admin')
    assert service.authenticate('new-admin', 'admin')


def test_credential_environment_variables_override_config(auth, monkeypatch):
    from werkzeug.security import generate_password_hash

    manager, service = auth
    env_hash = generate_password_hash('env-secret-pass', method='scrypt')
    monkeypatch.setenv('OPENYUGI_ADMIN_USERNAME', 'env-admin')
    monkeypatch.setenv('OPENYUGI_ADMIN_PASSWORD_HASH', env_hash)

    assert manager.get_auth_username() == 'env-admin'
    assert manager.get_auth_password_hash() == env_hash
    assert service.authenticate('env-admin', 'env-secret-pass')
    assert not service.authenticate('admin', 'admin')


def test_credentials_fall_back_to_config_without_environment_variables(auth, monkeypatch):
    manager, service = auth
    monkeypatch.delenv('OPENYUGI_ADMIN_USERNAME', raising=False)
    monkeypatch.delenv('OPENYUGI_ADMIN_PASSWORD_HASH', raising=False)

    assert manager.get_auth_username() == 'admin'
    assert service.authenticate('admin', 'admin')


def test_session_secret_is_stable_private_and_supports_environment_override(tmp_path):
    path = tmp_path / 'data' / '.storage_secret'
    first = get_storage_secret(path, {})
    second = get_storage_secret(path, {})

    assert first == second
    assert len(first) >= 32
    assert stat.S_IMODE(path.stat().st_mode) == 0o600
    assert get_storage_secret(path, {'OPENYUGI_STORAGE_SECRET': 'x' * 32}) == 'x' * 32
    with pytest.raises(ValueError, match='at least 32'):
        get_storage_secret(path, {'OPENYUGI_STORAGE_SECRET': 'too-short'})


def test_session_secret_creation_failure_has_actionable_error(tmp_path):
    path = tmp_path / 'data' / '.storage_secret'
    with patch('src.services.auth_service.os.open', side_effect=PermissionError('read-only')):
        with pytest.raises(RuntimeError, match='OPENYUGI_STORAGE_SECRET.*parent directory writable'):
            get_storage_secret(path, {})


def test_existing_config_permissions_are_tightened_on_startup(tmp_path):
    path = tmp_path / 'config.json'
    path.write_text(json.dumps({'auth_username': 'admin'}), encoding='utf-8')
    os.chmod(path, 0o644)

    ConfigManager(str(path))

    assert stat.S_IMODE(path.stat().st_mode) == 0o600


def test_login_nicegui_assets_and_well_known_uris_are_public():
    assert is_public_path('/login')
    assert is_public_path('/login/callback')
    assert is_public_path('/_nicegui_ws')
    assert is_public_path('/_nicegui/3.13.0/static/nicegui.js')
    assert is_public_path('/.well-known/appspecific/com.chrome.devtools.json')
    assert not is_public_path('/.well-known-attacker/anything')
    assert not is_public_path('/')
    assert not is_public_path('/settings')
    assert not is_public_path('/api/v1/collections')
    assert not is_public_path('/images/123.jpg')
    assert not is_public_path('/debug/scan.jpg')


@pytest.mark.parametrize(
    ('next_path', 'expected'),
    [
        ('/settings', '/settings'),
        ('/collection?page=2', '/collection?page=2'),
        ('https://example.com', '/'),
        ('//example.com', '/'),
        ('/\\example.com', '/'),
        ('/settings/\\example.com', '/'),
        ('/\t\\example.com', '/'),
        ('/\n\\example.com', '/'),
        ('/\r\\example.com', '/'),
        ('/settings\t', '/settings'),
        (None, '/'),
    ],
)
def test_login_next_path_is_restricted_to_local_paths(next_path, expected):
    assert _safe_next_path(next_path) == expected


@pytest.mark.asyncio
async def test_login_callback_rotates_session_and_redirects_to_safe_destination(monkeypatch):
    old_session = {
        TEMP_AUTH_TOKEN_KEY: 'temporary-token',
        TEMP_AUTH_TOKEN_EXPIRY_KEY: 1001,
    }
    new_session = {}

    class Storage:
        browser = {'id': 'old-session-id'}

        def __init__(self):
            self._created = AsyncMock()
            self._users = {'old-session-id': old_session, 'rotated-session-id': new_session}

        @property
        def user(self):
            return new_session if self.browser.get('id') == 'rotated-session-id' else old_session

        async def _create_user_storage(self, session_id):
            await self._created(session_id)

    storage = Storage()
    monkeypatch.setattr('src.ui.auth.app.storage', storage)
    monkeypatch.setattr('src.ui.auth.uuid.uuid4', lambda: 'rotated-session-id')
    monkeypatch.setattr('src.ui.auth.time.time', lambda: 1000)

    destination = await complete_login_callback('temporary-token', '/settings')

    assert destination == '/settings'
    assert storage.browser['id'] == 'rotated-session-id'
    storage._created.assert_awaited_once_with('rotated-session-id')
    assert new_session[AUTH_SESSION_KEY] is True
    assert new_session[AUTH_REVISION_KEY]
    assert old_session == {}
    assert 'old-session-id' not in storage._users


@pytest.mark.asyncio
async def test_login_callback_rejects_invalid_token(monkeypatch):
    session = {
        TEMP_AUTH_TOKEN_KEY: 'temporary-token',
        TEMP_AUTH_TOKEN_EXPIRY_KEY: 1001,
    }

    class Storage:
        user = session

    monkeypatch.setattr('src.ui.auth.app.storage', Storage())
    monkeypatch.setattr('src.ui.auth.time.time', lambda: 1000)

    assert await complete_login_callback('wrong-token', '/settings') is None


@pytest.mark.asyncio
async def test_login_callback_rejects_and_consumes_expired_token(monkeypatch, caplog):
    session = {
        TEMP_AUTH_TOKEN_KEY: 'temporary-token',
        TEMP_AUTH_TOKEN_EXPIRY_KEY: 999,
    }

    class Storage:
        user = session
        browser = {}

    monkeypatch.setattr('src.ui.auth.app.storage', Storage())
    monkeypatch.setattr('src.ui.auth.time.time', lambda: 1000)

    with caplog.at_level(logging.WARNING, logger='src.ui.auth'):
        assert await complete_login_callback('temporary-token', '/settings') is None

    assert TEMP_AUTH_TOKEN_KEY not in session
    assert TEMP_AUTH_TOKEN_EXPIRY_KEY not in session
    assert 'expired login callback token' in caplog.text


@pytest.mark.asyncio
async def test_login_callback_replay_is_rejected_and_logged(monkeypatch, caplog):
    session = {}

    class Storage:
        user = session
        browser = {}

    monkeypatch.setattr('src.ui.auth.app.storage', Storage())

    with caplog.at_level(logging.WARNING, logger='src.ui.auth'):
        assert await complete_login_callback('already-consumed-token', '/settings') is None

    assert 'replayed or consumed login callback token' in caplog.text


def test_main_app_redirects_unauthenticated_routes_to_login():
    set_storage_secret('test-storage-secret-that-is-at-least-32-characters')
    client = TestClient(main.app, follow_redirects=False)
    try:
        for path in ('/', '/settings', '/images/123.jpg', '/debug/scan.jpg'):
            response = client.get(path)
            assert response.status_code == 303
            assert response.headers['location'].startswith('/login?next=')

        response = client.get('/api/v1/collections')
        assert response.status_code == 401
        assert response.json() == {'detail': 'Not authenticated'}

        response = client.get('/.well-known/appspecific/com.chrome.devtools.json')
        assert response.status_code == 200
        assert response.json() == {}

    finally:
        client.close()
