from unittest.mock import AsyncMock, patch

import pytest

from src.ui import collection


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('viewport_width', 'expected_page_size'),
    [
        (390, collection.COLLECTION_MOBILE_PAGE_SIZE),
        (1024, collection.COLLECTION_DESKTOP_PAGE_SIZE),
    ],
)
async def test_collection_uses_responsive_page_size(viewport_width, expected_page_size):
    page = collection.CollectionPage.__new__(collection.CollectionPage)
    page.state = {'page': 3, 'page_size': 99}

    with patch.object(
        collection.ui,
        'run_javascript',
        new=AsyncMock(return_value=viewport_width),
    ):
        await page._set_responsive_page_size()

    assert page.state == {'page': 1, 'page_size': expected_page_size}


def test_collection_mobile_page_size_is_twelve():
    assert collection.COLLECTION_MOBILE_PAGE_SIZE == 12
