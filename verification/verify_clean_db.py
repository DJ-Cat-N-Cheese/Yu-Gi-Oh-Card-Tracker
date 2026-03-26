import sys
import asyncio
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['requests'] = MagicMock()
sys.modules['cv2'] = MagicMock()
sys.modules['ultralytics'] = MagicMock()

import nicegui
from nicegui import ui, app, Client
from src.ui.layout import create_layout

@ui.page('/')
def index_page():
    def dummy_content():
        ui.label("Main Content Area")
    create_layout(dummy_content)

ui.run(port=8080, show=False, dark=True)
