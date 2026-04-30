import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

# Let's fix the bind value to ensure on_change gets executed initially but through nicegui bind
# NiceGUI image components can act weird. A solid fix is to recreate it or just use an HTML block.
content = content.replace("img.classes(remove='hidden', add='block')", "img.classes(remove='hidden').classes(add='block')")

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
