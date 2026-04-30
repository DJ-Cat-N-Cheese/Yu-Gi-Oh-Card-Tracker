import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

# Make sure image.source receives string correctly, nicegui uses .source prop under the hood but some older versions need to call img.set_source() explicitly. We will provide it via set_source if possible, or direct source assignment.
content = content.replace("img.source = img_map[val]", "img.set_source(img_map[val]) if hasattr(img, 'set_source') else setattr(img, 'source', img_map[val])")

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
