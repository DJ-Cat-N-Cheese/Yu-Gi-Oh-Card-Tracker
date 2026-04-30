with open("src/ui/db_editor.py", "r") as f:
    content = f.read()

content = content.replace(
    "close_btn = ui.button('Close', on_click=dialog.close).props('color=primary').classes('mt-4 w-full').set_visibility(False)",
    "close_btn = ui.button('Close', on_click=dialog.close).props('color=primary').classes('mt-4 w-full')\n            close_btn.set_visibility(False)"
)

with open("src/ui/db_editor.py", "w") as f:
    f.write(content)
