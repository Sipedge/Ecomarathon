from data import Config
from alerts import AlertDialog_spawn
import flet as ft
from websockets_orm import websocket
from utils import exit_app, go_back


async def create_lobby_def(config: Config, page: ft.Page): 
    async def go_back_def(e):
        await go_back(e, config)

    if config._errors:
        alert = AlertDialog_spawn(config._errors,"Ок", my_page=page)
        alert.alert_spawn(config)
        return 0

    await page.push_route("/lobby_view")
    await websocket.connect(config, page)
    
    

    if config._errors:
        alert = AlertDialog_spawn(config._errors, "Выйти из лобби", my_page=page, on_click=go_back_def)
        alert.alert_spawn(config)
        return 0
    
    
    

    


    