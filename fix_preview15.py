import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

# I will replace ui.image with an HTML img tag to ensure it works across all NiceGUI versions with 100% certainty if ui.image props are failing to bind correctly.
content = content.replace("preview_image = ui.image('').classes('w-48 h-auto mt-2 hidden rounded')", "preview_image = ui.html('<img src=\"\" style=\"max-width: 12rem; height: auto; border-radius: 0.25rem;\" />').classes('mt-2 hidden')")
content = content.replace("img.props(f'src=\"{img_map[val]}\"')", "img.content = f'<img src=\"{img_map[val]}\" style=\"max-width: 12rem; height: auto; border-radius: 0.25rem;\" />'")

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
