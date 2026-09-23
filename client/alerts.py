import flet as ft
from data import Config

class AlertDialog_spawn(ft.AlertDialog):
    def __init__(self, text: str, text_button: str, my_page: ft.Page, on_click=None):
        super().__init__()
        
        self._page = my_page
        self.text = text
        self.text_button = text_button
        self.title = ft.Text("Ошибка клиента") 
        self.content = ft.Text(self.text)
        self.modal = True
        
        if on_click is None:
            handler = lambda e: self.close(e)
        else:
            handler = on_click
        self.actions = [ft.Button(self.text_button, on_click=handler)]
        self.open = True 

    def close(self, e):
        self.open = False
        self._page.update()

    def alert_spawn(self, config: Config):
        self._page.overlay[:] = [c for c in self._page.overlay if not isinstance(c, AlertDialog_spawn)]
        self._page.overlay.append(self)
        self.open = True
        self._page.update()
        config._errors = ""