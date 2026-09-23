import flet as ft
from instuments import server_create_user, create_server
from data import Config
from alerts import AlertDialog_spawn
from utils import exit_app, go_back
from websockets_orm import websocket
from views.spawn_lobby import create_lobby_def 


_username_field = ft.TextField(
    label="Введите имя",
    color="#000000",
    width=400,          
    autofocus=True,         
    border_radius=30,              
    filled=True,                  
    bgcolor="#F3FCF4",                
    border_color="#4CAF50",        
    hint_text="Имя...",
    max_length=20             
)


class CreateUserConnect(ft.View):
    def __init__(self, config: Config):
        super().__init__(route="/create_user_connect", padding=0) 
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
                                _username_field,
                                ft.Button(
                                    bgcolor="#82D685",
                                    on_click=self.create,
                                    width=400, 
                                    height=45,                  
                                    content=ft.Text(
                                        "Ввести",
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
        await go_back(e, self.config)

    async def create(self, e):
        await server_create_user(self.config, _username_field.value)
        if self.config._errors == "Домен/IP указан неверно":
            alert = AlertDialog_spawn(self.config._errors, exit_app, 'Выход')
            alert.alert_spawn(self.config)
            return 0
        if self.config._errors == "Такое имя уже занято. Введите другое имя.":
            alert = AlertDialog_spawn(text=self.config._errors, text_button='Ок', my_page=e.page)
            alert.alert_spawn(self.config)
            return 0
        await e.page.push_route("/connect")        
        
        
        

    