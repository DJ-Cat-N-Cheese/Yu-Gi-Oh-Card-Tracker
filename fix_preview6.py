import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

content = content.replace("img.source = img_map[val]", "img.set_source(img_map[val])")
content = content.replace("select = ui.select(options, label=\"Select Variant\", on_change=on_change).bind_value(item, 'selected_variant_id').classes('w-full')", "select = ui.select(options, label=\"Select Variant\", on_change=on_change).classes('w-full')\n                                            select.bind_value(item, 'selected_variant_id')\n                                            if item.get('selected_variant_id'):\n                                                on_change(type('obj', (object,), {'value': item['selected_variant_id']}))")

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
