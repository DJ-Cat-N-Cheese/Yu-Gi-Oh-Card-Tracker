from nicegui import ui

class MyPage:
    @ui.refreshable
    def my_content(self):
        ui.label('Content')

    def build(self):
        self.my_content()

@ui.page('/')
def index():
    p = MyPage()
    p.build()

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(port=8081)
