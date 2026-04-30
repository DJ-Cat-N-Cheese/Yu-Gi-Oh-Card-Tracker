import re

with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

# I will replace the ui.image update logic with dynamic container clearing which is the most robust way to show images in NiceGUI dialogs where component lifecycle gets confusing.
old_block = """                                            # Use the actual card ID to get the default image immediately to prevent placehold missing picture, then swap out for correct one.
                                            preview_image = ui.image(f"/api/images/{item['card_id']}").classes('w-32 h-auto mt-2 hidden object-contain rounded shadow')

                                            def on_change(e, img=preview_image, img_map=var_images):
                                                val = e.value
                                                if val and val in img_map:
                                                    img.source = img_map[val]
                                                    img.classes(remove='hidden', add='block')
                                                    img.update()
                                                else:
                                                    img.classes(add='hidden')
                                                    img.update()"""

new_block = """                                            preview_container = ui.column().classes('mt-2')

                                            def on_change(e, cont=preview_container, img_map=var_images):
                                                val = e.value
                                                cont.clear()
                                                if val and val in img_map:
                                                    with cont:
                                                        ui.image(img_map[val]).classes('w-32 h-auto object-contain rounded shadow')"""

content = content.replace(old_block, new_block)

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
