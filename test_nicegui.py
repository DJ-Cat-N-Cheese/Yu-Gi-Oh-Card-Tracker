from nicegui import ui
btn = ui.button('Close')
res = btn.set_visibility(False)
print("Result of set_visibility:", res)
