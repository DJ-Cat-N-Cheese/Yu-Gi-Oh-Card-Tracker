from nicegui import ui

def handle_upload(e):
    print("Event type:", type(e))
    print("Dir e:", dir(e))
    print("e.name hasattr?", hasattr(e, 'name'))
    # Stop the app to exit test
    ui.timer(0.1, lambda: app.shutdown())

ui.upload(on_upload=handle_upload, auto_upload=True)

# we just want to inspect the arguments structure
