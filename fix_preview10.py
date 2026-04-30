import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

# Wait, if nicegui ui.image is not showing, it might be due to lazy loading or props.
# Let's force it to update props if necessary.
# Also remove 'hidden' class string correctly and add a default background to check if component renders.

content = content.replace("img.classes(remove='hidden')", "img.classes(remove='hidden').classes(add='block bg-gray-800')")

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
