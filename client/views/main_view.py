import flet as ft
from utils import exit_app
import os
from pathlib import Path

class MainView(ft.View):
    def __init__(self):
        super().__init__(route="/", padding=0) 
        
        def btn(text: str, on_click=None):
            return ft.Container(
                content=ft.Text(
                    text,
                    style=ft.TextStyle(
                        shadow=ft.BoxShadow(blur_radius=2, offset=ft.Offset(2,2), color="#808080"),
                        size=30,
                        weight=ft.FontWeight.W_900,
                        color="#234746"
                    ),
                ),
                on_click=on_click,
            )
            
        self.create_lobbuser = btn("Создать лобби", on_click=self.create_user)
        self.join_lobby_btn = btn("Присоединиться", on_click=self.connect)
        self.docs_btn = btn("Документация", on_click=self.docs)
        self.exit_btn = btn("Выход", on_click=exit_app)
        
        self.controls = [
            ft.Stack(
                [
                    ft.Container(
                        expand=True,
                        image=ft.DecorationImage(
                            src=r"..\assets\Главное меню.png",
                            fit=ft.BoxFit.FILL,
                            )
                        ),

                    ft.Container(
                        alignment=ft.alignment.Alignment.BOTTOM_LEFT,
                        padding=60,
                        content=ft.Column(
                            [
                                self.create_lobbuser,
                                self.join_lobby_btn,
                                self.docs_btn,
                                self.exit_btn,
                            ],
                            spacing=10,
                            tight=True
                        ),
                    )
                ],
                expand=True,
            )
        ]
    

    async def create_user(self, e):
        await e.page.push_route('/create_user')

    async def connect(self, e):
        await e.page.push_route('/create_user_connect')

    def docs(self, e=None):
        # Определяем путь к файлу относительно данного скрипта
        current_file = Path(__file__)                     # .../client/views/main_view.py
        assets_dir = current_file.parent.parent / "assets" # .../client/assets/
        doc_file = assets_dir / "Документация.chm"

        if doc_file.exists():
            os.startfile(str(doc_file))