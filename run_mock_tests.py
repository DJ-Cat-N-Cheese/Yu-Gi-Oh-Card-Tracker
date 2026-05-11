import sys
from unittest.mock import MagicMock

# Mock out required dependencies
sys.modules['pydantic'] = MagicMock()
sys.modules['nicegui'] = MagicMock()
sys.modules['aiohttp'] = MagicMock()
sys.modules['bs4'] = MagicMock()

import pytest

if __name__ == "__main__":
    pytest.main(["tests/"])
