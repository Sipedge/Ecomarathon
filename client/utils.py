import flet as ft


async def exit_app(e):
    await e.page.window.close()

lobby = None
game = None

async def go_back(e, config, page = "/"):
    global lobby
    lobby = None
    global game
    game = None
    config.code = 0
    target_page = e.page
    
    if target_page:
        await target_page.push_route(page)
    return config.code

