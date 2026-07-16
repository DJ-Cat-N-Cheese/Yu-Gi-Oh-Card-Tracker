import pytest

from src.core.models import Collection
from src.core.persistence import PersistenceManager, sanitize_collection_filename


def test_sanitize_collection_filename_accepts_plain_filename():
    assert sanitize_collection_filename('  My Collection.json  ') == 'My Collection.json'


@pytest.mark.parametrize(
    'filename',
    [
        '../escaped.json',
        '..\\escaped.json',
        'nested/escaped.json',
        'nested\\escaped.json',
        'collection..json',
    ],
)
def test_sanitize_collection_filename_rejects_path_components(filename):
    with pytest.raises(ValueError, match='path separators|Invalid collection'):
        sanitize_collection_filename(filename)


@pytest.mark.parametrize(
    'filename',
    [
        'evil\0name.json',
        '\0.json',
        '%00escaped.json',
    ],
)
def test_sanitize_collection_filename_rejects_null_bytes(filename):
    with pytest.raises(ValueError, match='null bytes'):
        sanitize_collection_filename(filename)


@pytest.mark.parametrize(
    'filename',
    [
        '%2e%2e%2fescaped.json',
        '%2E%2E%2Fescaped.json',
        '%2e%2e%5cescaped.json',
        '%2e%2e/escaped.json',
        '..%2fescaped.json',
        '%252e%252e%252fescaped.json',  # double URL-encoded
    ],
)
def test_sanitize_collection_filename_rejects_url_encoded_traversal(filename):
    with pytest.raises(ValueError, match='path separators|Invalid collection'):
        sanitize_collection_filename(filename)


@pytest.mark.parametrize(
    'filename',
    [
        '．．／escaped.json',  # fullwidth dots + fullwidth solidus
        '．．/escaped.json',  # fullwidth dots + literal slash
        '‥／escaped.json',  # two-dot leader + fullwidth solidus
        'collection․․json',  # one-dot leaders normalize to '..'
    ],
)
def test_sanitize_collection_filename_rejects_unicode_lookalikes(filename):
    with pytest.raises(ValueError, match='path separators|Invalid collection'):
        sanitize_collection_filename(filename)


def test_save_collection_rejects_path_traversal(tmp_path):
    collections_dir = tmp_path / 'collections'
    manager = PersistenceManager(
        data_dir=str(collections_dir),
        decks_dir=str(tmp_path / 'decks'),
    )

    with pytest.raises(ValueError, match='path separators'):
        manager.save_collection(Collection(name='Escaped'), '../escaped.json')

    assert not (tmp_path / 'escaped.json').exists()
