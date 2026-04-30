import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

# Let's verify standard HTML img instead of ui.image inside the container. NiceGUI ui.image inside dialogs is notoriously buggy across versions when generated dynamically.
old_block = """                                                    with cont:
                                                        ui.image(img_map[val]).classes('w-32 h-auto object-contain rounded shadow')"""

new_block = """                                                    with cont:
                                                        ui.html(f'<img src="{img_map[val]}" class="w-48 h-auto rounded shadow border border-gray-700" />')"""

content = content.replace(old_block, new_block)

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
