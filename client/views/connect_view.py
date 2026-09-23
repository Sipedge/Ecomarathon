import flet as ft
from instuments import server_create_user, create_server
from data import Config
from alerts import AlertDialog_spawn
from utils import exit_app, go_back
from websockets_orm import websocket
from views.spawn_lobby import create_lobby_def 


_code_field = ft.TextField(
            label="Введите код",
            color="#000000",
            width=400,          
            autofocus=True,         
            border_radius=30,              
            filled=True,                  
            bgcolor="#F3FCF4",                
            border_color="#4CAF50",        
            hint_text="Код...",
            max_length=5           
        )


class ConnectLobby(ft.View):
    def __init__(self, config: Config):
        super().__init__(route="/connect", padding=0) 
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
                    ft.Container(
                        bgcolor="#E4FAE6",
                        border_radius=30,
                        padding=20,
                        width=500,
                        height=300,
                        alignment=ft.Alignment.CENTER,
                        content=ft.Column(
                            controls=[
                                _code_field,
                                ft.Button(
                                    bgcolor="#82D685",
                                    on_click=self.connect,
                                    width=400, 
                                    height=45,                  
                                    content=ft.Text(
                                        "Присоединиться",
                                            style=ft.TextStyle(
                                            size=20,
                                            weight=ft.FontWeight.W_900,
                                            color="#234746"
                                        ),
                                    ),
                                )
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,        
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,  
                        )
                    ),
                    
                ],
                expand=True,
                alignment=ft.Alignment.CENTER
            )
        ]
        
    async def go_back(self, e):
        await websocket.close(self.config)
        await go_back(e, self.config)
        

    async def connect(self, e):
        self.config.code = _code_field.value
        await create_lobby_def(self.config, e.page)
        
        
        
        

    