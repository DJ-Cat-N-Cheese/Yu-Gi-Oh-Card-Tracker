from nicegui import ui

def main():
    options = {1: 'One', 2: 'Two', 3: 'Three'}
    select = ui.select(options, label='Select Number')
    preview_image = ui.image('https://placehold.co/400').classes('w-32 h-auto mt-2 hidden')

    def on_change(e):
        val = e.args if hasattr(e, 'args') else e.value if hasattr(e, 'value') else e.sender.value
        print(f"on_change triggered. Event type: {type(e)}, val: {val}")
        if val:
            preview_image.classes(remove='hidden')
            preview_image.source = f'https://placehold.co/400?text={val}'
        else:
            preview_image.classes(add='hidden')

    select.on('update:model-value', on_change)

ui.run(port=8080)
