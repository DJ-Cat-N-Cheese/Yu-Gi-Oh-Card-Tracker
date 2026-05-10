import sys
from unittest.mock import MagicMock

sys.modules['nicegui'] = MagicMock()
sys.modules['nicegui.ui'] = MagicMock()
sys.modules['nicegui.events'] = MagicMock()

import pytest
from unittest.mock import patch, AsyncMock
import json
from src.ui.import_tools import UnifiedImportController

@pytest.fixture
def mock_dependencies():
    with patch('src.ui.import_tools.persistence') as mock_persistence, \
         patch('src.ui.import_tools.ygo_service') as mock_ygo, \
         patch('src.ui.import_tools.ui') as mock_ui, \
         patch('src.services.pricing_service.pricing_service') as mock_pricing:

         # Mock internal local data
         mock_pricing.daily_pricing = {}
         mock_pricing.offers_pricing = {}

         yield mock_persistence, mock_ygo, mock_ui, mock_pricing

@pytest.mark.asyncio
async def test_process_pricing_daily(mock_dependencies):
    mock_persistence, mock_ygo, mock_ui, mock_pricing = mock_dependencies

    controller = UnifiedImportController()

    # Valid daily pricing JSON
    data = {
        "123": {
            "variant-1": {
                "cardmarket": {
                    "2023-10-10": 1.5
                }
            }
        }
    }
    content = json.dumps(data).encode('utf-8')

    await controller.process_pricing(content)

    assert controller.pricing_import_type == 'daily'
    assert len(controller.pricing_preview) == 1
    assert controller.pricing_preview[0]['added'] == 1
    assert controller.pricing_preview[0]['updated'] == 0

@pytest.mark.asyncio
async def test_apply_pricing_import(mock_dependencies):
    mock_persistence, mock_ygo, mock_ui, mock_pricing = mock_dependencies

    controller = UnifiedImportController()
    controller.import_type = 'PRICING'
    controller.pricing_import_type = 'daily'
    controller.pricing_overwrite = True
    controller.pricing_data_to_import = {
        "123": {
            "variant-1": {
                "cardmarket": {
                    "2023-10-10": 1.5,
                    "2023-10-11": 2.0
                }
            }
        }
    }

    # Simulate existing data
    mock_pricing.daily_pricing = {
        "123": {
            "variant-1": {
                "cardmarket": {
                    "2023-10-10": 1.0 # Should be overwritten
                }
            }
        }
    }

    await controller.apply_import()

    assert mock_pricing._save_json.called
    saved_data = mock_pricing._save_json.call_args[0][1]

    # Verify the merge
    assert saved_data["123"]["variant-1"]["cardmarket"]["2023-10-10"] == 1.5
    assert saved_data["123"]["variant-1"]["cardmarket"]["2023-10-11"] == 2.0
