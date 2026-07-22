import logging
import os
from pathlib import Path

import nicegui
import PyInstaller.__main__

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Get the path to nicegui so we can include its static assets
nicegui_dir = Path(nicegui.__file__).parent

logger.info('Starting PyInstaller build for OpenYuGi')
PyInstaller.__main__.run([
    'main.py',
    '--name=OpenYuGi',
    '--onedir',
    # Do not use windowed mode since we want NiceGUI to launch the browser and show logs
    '--console',
    f'--add-data={nicegui_dir}{os.pathsep}nicegui',
    '--clean',
    '--noconfirm',
])
logger.info('PyInstaller build completed successfully')
