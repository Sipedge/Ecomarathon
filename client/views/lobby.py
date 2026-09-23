import flet as ft
from data import Config
import pyperclip
from websockets_orm import websocket
from alerts import AlertDialog_spawn
from utils import go_back


class LobbyView(ft.View):
    
    def __init__(self, config: Config):
        super().__init__(route="/lobby_view", padding=0)

        self.usernames_column = ft.Column(spacing=10)
        self.usernames_container = ft.Container(
            bgcolor="#E4FAE6",
            border_radius=30,
            padding=20,
            width=500,
            height=300,
            content=ft.Column([
                ft.Text("Пользователи в лобби:", 
                        style=ft.TextStyle(
                        shadow=ft.BoxShadow(blur_radius=2, offset=ft.Offset(2,2), color="#808080"),
                        size=25,
                        weight=ft.FontWeight.W_900,
                        color="#234746"),),
                self.usernames_column
            ], scroll=ft.ScrollMode.AUTO)
        )
        self.config = config
        self.expand = True
        self.bgcolor="#F5EAD4"
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.controls = [
            ft.Stack(
                [
                    ft.Container(
                        alignment=ft.alignment.Alignment.TOP_LEFT,
                        padding=20,
                        content=ft.Column(
                            [
                                ft.IconButton(
                                    icon=ft.Icons.ARROW_BACK_OUTLINED,
                                    on_click=self.go_back,
                                    icon_size = 30,
                                    icon_color="#234746"
                                ),
                            ],
                            tight=True
                        ),
                    ),


                    ft.Column([
                        ft.Container(
                            content=ft.Row([
                                ft.Text("Код:", weight=ft.FontWeight.W_700, size = 20, color="#234746"),
                                ft.Text(str(self.config.code), size=20, weight=ft.FontWeight.W_700, color="#234746"),
                                ft.IconButton(
                                   icon=ft.Icons.COPY,
                                   on_click=lambda e: pyperclip.copy(self.config.code), # замени на переменную с кодом
                                )
                            ], alignment=ft.Alignment.CENTER),
                            border_radius=15,
                            padding=10,
                            width=500,
                            alignment=ft.Alignment.CENTER,
                        ),
                        self.usernames_container,
                        ft.Button(
                            bgcolor="#82D685",
                            on_click=self.ready,
                            width=500, 
                            height=45,                  
                            content=ft.Text(
                                "Готов",
                                    style=ft.TextStyle(
                                    size=20,
                                    weight=ft.FontWeight.W_900,
                                    color="#234746"
                                ),
                            ),
                        )
                    ],
                    horizontal_alignment = ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                    run_alignment=ft.MainAxisAlignment.CENTER,
                    expand=True
                    )
                ],
                alignment = ft.Alignment.CENTER,
                expand=True,
            )
        ]
        
    async def go_back(self, e):
        await websocket.close(self.config)
        await go_back(e, self.config)
        

    def update_users(self, usernames: list[str], list_ready: list[int]):
        self.usernames_column.controls.clear()
        count = 0
        display_names = list(usernames)
        for idx in list_ready:
            if 0 <= idx < len(display_names):
                display_names[idx] += " (Готов)"
    
        for user in display_names:
            count += 1
            self.usernames_column.controls.append(
                ft.Text(
                    f"{count}) {user}",
                    style=ft.TextStyle(
                        shadow=ft.BoxShadow(blur_radius=2, offset=ft.Offset(1,1), color="#808080"),
                        size=15,
                        weight=ft.FontWeight.W_600,
                        color="#234746"
                    ),
                )
            )
        if self.page:
            self.usernames_column.update()
        else:
            pass

    async def ready(self):
        websocket.send_action("ready", username = self.config.username)

    async def start(self):
        await self.page.push_route('/game')

    async def alert_await(self):
        alert = AlertDialog_spawn("Игра уже началась", text_button="Ок", my_page=self.page, on_click=self.go_back)
        alert.alert_spawn(self.config)

    async def alert_bancrut(self): 
        alert = AlertDialog_spawn("Вы обонкротились.", text_button="Ок", my_page=self.page, on_click=self.go_back)
        alert.alert_spawn(self.config)

    async def lobby_full(self):
        alert = AlertDialog_spawn("Лобби заполнено", text_button="Ок", my_page=self.page, on_click=self.go_back)
        alert.alert_spawn(self.config)

