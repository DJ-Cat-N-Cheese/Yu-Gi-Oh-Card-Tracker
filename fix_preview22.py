import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

# Make sure the container takes up no vertical space when empty.
# In NiceGUI/Tailwind, ui.column has gaps. We can remove the gap or just rely on the image inside.
old_block = "preview_container = ui.column().classes('mt-2')"
new_block = "preview_container = ui.element('div').classes('mt-2')"

content = content.replace(old_block, new_block)

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
