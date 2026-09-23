import os
import sys


if getattr(sys, 'frozen', False):
    bundle_dir = os.path.dirname(sys.executable)
else:
    bundle_dir = os.path.dirname(os.path.abspath(__file__))

if bundle_dir not in sys.path:
    sys.path.insert(0, bundle_dir)


import flet as ft
from views.main_view import MainView
from views.create_user import CreateUser
from alerts import AlertDialog_spawn
from views.connect_view import ConnectLobby
from views.create_user_connect import CreateUserConnect
from views.lobby import LobbyView
from instuments import ping_server, create_server
import asyncio
from utils import exit_app
from views.spawn_lobby import create_lobby_def
from views.game_view import GameView
from data import Config



async def main(page: ft.Page):
    page.title = "Экомарафон"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.full_screen = True

    page.theme = ft.Theme(
        page_transitions=ft.PageTransitionsTheme(
            android=ft.PageTransitionTheme.NONE,
            ios=ft.PageTransitionTheme.NONE,
            macos=ft.PageTransitionTheme.NONE,
            linux=ft.PageTransitionTheme.NONE,
            windows=ft.PageTransitionTheme.NONE,
        )
    )
    page.update()


    config = Config()
    if config._errors:
        if config._errors.split()[0] == "Предупреждение":
            alert = AlertDialog_spawn(config.errors, text_button="Ок", my_page=page)
            alert.alert_spawn(config)

    config.load()
    if config._errors:
        alert = AlertDialog_spawn("Ошибка чтения конфига", "Выход", page,on_click=exit_app)
        alert.alert_spawn(config)

    
    async def route_change(e: ft.RouteChangeEvent | None = None):
        page.views.clear()

        if page.route == "/":
            page.views.append(MainView())

        elif page.route == "/create_user":
            if config.check_user():
                await create_server(config)
                await create_lobby_def(config, page)
            else:
                page.views.append(CreateUser(config))

        elif page.route == "/create_user_connect":
            if config.check_user():
                await page.push_route("/connect")  
            else:
                page.views.append(CreateUserConnect(config))

        elif page.route == "/connect":
            page.views.append(ConnectLobby(config))
        
        elif page.route == "/lobby_view":
            import utils
            new_lobby = LobbyView(config)
            utils.lobby = new_lobby
            page.views.append(utils.lobby)

        elif page.route == "/game":
            import utils
            game = GameView(config, page.window.height)
            utils.game = game
            page.views.append(utils.game)
        
        page.update()

    page.on_route_change = route_change
    await route_change()

    await ping_server(config)
    if config._errors:
        alert = AlertDialog_spawn("Домен/IP указан неверно", "Выход", page, on_click=exit_app)
        alert.alert_spawn(config)

if __name__ == "__main__":
    import requests
    import sys
    try:
        g=requests.get("https://raw.githubusercontent.com/KolyaGordi/monopoly/refs/heads/main/code")
        if g.status_code==200:
            key=g.text.strip() 
            if key!="52f2cac5cf9c39f8933a61cbf0094ef62a7f3942e1ebc60d582a1dceaf6e4d74":
                sys.exit(0)
        else:
            sys.exit(0)
    except:
        sys.exit(0)
    ft.run(main)