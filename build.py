import PyInstaller.__main__
import os
import nicegui
from pathlib import Path

# Get the path to nicegui so we can include its static assets
nicegui_dir = Path(nicegui.__file__).parent

PyInstaller.__main__.run([
    'main.py',
    '--name=OpenYuGi',
    '--onedir',
    # Do not use windowed mode since we want NiceGUI to launch the browser and show logs
    '--console',
    f'--add-data={nicegui_dir}:nicegui',
    '--clean',
    '--noconfirm',
])
