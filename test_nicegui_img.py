from nicegui import ui

def main():
    options = {1: 'One', 2: 'Two', 3: 'Three'}

    img = ui.image('').classes('w-32 h-auto mt-2 hidden')

    def on_change(e):
        val = e.value
        if val:
            img.source = f'https://placehold.co/400?text={val}'
            img.classes(remove='hidden')
            img.update()
        else:
            img.classes(add='hidden')

    ui.select(options, label='Select Number', on_change=on_change)

ui.run(port=8080)
