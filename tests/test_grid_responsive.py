import pytest

from src.ui import browse_sets, collection, storage, theme

GRIDS = [collection.CARD_GRID_COLUMNS, theme.TILE_GRID_COLUMNS]


@pytest.mark.parametrize('grid_classes', GRIDS)
def test_grids_start_at_two_columns_on_phones(grid_classes):
    # The unprefixed class is the phone case; anything denser squeezes a tile
    # below ~155px at a 390px viewport.
    assert grid_classes.split()[0] == 'grid-cols-2'


@pytest.mark.parametrize('grid_classes', GRIDS)
def test_grid_column_counts_increase_with_breakpoint(grid_classes):
    counts = [int(c.rsplit('-', 1)[1]) for c in grid_classes.split()]
    assert counts == sorted(counts)


def test_card_grids_reuse_the_collection_ladder():
    # Storage and set detail views show the same card art as the collection,
    # so they must not drift from its column ladder.
    assert storage.CARD_GRID_COLUMNS is collection.CARD_GRID_COLUMNS
    assert browse_sets.CARD_GRID_COLUMNS is collection.CARD_GRID_COLUMNS


def test_tile_grid_is_sparser_than_card_grid():
    # Cover-art tiles are wider than cards, so they must never be denser.
    def widest(classes):
        return int(classes.split()[-1].rsplit('-', 1)[1])

    assert widest(theme.TILE_GRID_COLUMNS) < widest(collection.CARD_GRID_COLUMNS)
