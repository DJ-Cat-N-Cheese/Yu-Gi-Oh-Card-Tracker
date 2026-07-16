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


def test_save_collection_rejects_path_traversal(tmp_path):
    collections_dir = tmp_path / 'collections'
    manager = PersistenceManager(
        data_dir=str(collections_dir),
        decks_dir=str(tmp_path / 'decks'),
    )

    with pytest.raises(ValueError, match='path separators'):
        manager.save_collection(Collection(name='Escaped'), '../escaped.json')

    assert not (tmp_path / 'escaped.json').exists()
