import httpx
from data import Config

async def server_create_user(config: Config, user: str):
    data = {"username": user}
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.post(f'{config.domen}/users/create', data=data)
            if "username" in response.json().keys():
                username = response.json().get("username")
                config.username = username
            if response.status_code == 422:
                config._errors = "Такое имя уже занято. Введите другое имя."
        except (httpx.ConnectError, httpx.UnsupportedProtocol):
            config._errors = "Домен/IP указан неверно"

async def ping_server(config: Config):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.head(f"{config.domen}/users/ping", timeout=0.2)
            if "X-Ping" not in response.headers.keys():
                if response.headers.get("X-Ping") != "Connect":
                    config._errors = "Домен/IP указан неверно"
            else:
                config._errors = "Домен/IP указан неверно"
        except (httpx.ConnectError, httpx.UnsupportedProtocol, httpx.TimeoutException, httpx.ConnectError):
            config._errors = "Домен/IP указан неверно"

async def create_server(config: Config):
    async with httpx.AsyncClient() as client:
        try: 
            response = await client.post(f"{config.domen}/lobby/create")
            if response.status_code == 503:
                config._errors = "Создано макчимальное количесвто лобби. Подождите завершения одной из игры"
                return 0
            else:
                config.code = int(response.text)
                return int(response.text)
        except Exception as e:
            config._errors = "Что-то пошло не так при создании сервера."
            return 0 
        

        
            


            
    
