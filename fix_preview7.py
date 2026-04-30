import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

# Revert to standard nicegui format to rule out `set_source` breaking properties:
content = content.replace("img.set_source(img_map[val])", "img.source = img_map[val]")

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
