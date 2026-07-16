import json
import os
import stat
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from nicegui.storage import set_storage_secret
from werkzeug.security import check_password_hash

import main
from src.core.config import ConfigManager
from src.services.auth_middleware import is_public_path
from src.services.auth_service import AuthService, get_storage_secret
from src.ui.auth import _safe_next_path


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
        (None, '/'),
    ],
)
def test_login_next_path_is_restricted_to_local_paths(next_path, expected):
    assert _safe_next_path(next_path) == expected


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
