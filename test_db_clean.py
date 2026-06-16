import sys
from unittest.mock import MagicMock
sys.modules['pydantic'] = MagicMock()
sys.modules['nicegui'] = MagicMock()

from src.core.utils import is_set_code_compatible

def test_clean_logic():
    lang = "de"

    assert is_set_code_compatible("LOB-G001", lang) == True
    assert is_set_code_compatible("LOB-EN001", lang) == False
    assert is_set_code_compatible("LOB-001", lang) == True

    print("Test passed!")

if __name__ == "__main__":
    test_clean_logic()
