from pydantic import BaseModel, PrivateAttr
import json
import os, sys
from pathlib import Path


def get_resource_path(filename):
    if getattr(sys, 'frozen', False):
        print(sys.frozen())
        datadir = os.path.dirname(sys.executable)
    else:
        datadir = os.path.dirname(__file__)
    return Path(datadir) / filename

ip_path = get_resource_path("ip_domen_server.txt")
BASE_DIR = Path(__file__).parent

class Config(BaseModel):
    code: int = 0
    username: str = ""
    domen: str = ""
    ws_domen: str = ""
    _errors : str = PrivateAttr('')
    usernames : list[str] = []
    money : list[int] = []
    
    def __init__(self, **data):
        super().__init__(**data)
        self.load_server_domen()

    def load_server_domen(self):
        try: 
            if ip_path.exists():
                with open(ip_path, "r", encoding="utf-8") as file:
                    ip = file.read().strip()
                self.domen = f"http://{ip}"
                self.ws_domen = f"ws://{ip}"
            else:
                self._errors = f"Предупреждение: Файл {ip_path} не найден. Использую http://localhost:8000"
                self.domen = "http://localhost:8000"
                self.ws_domen = "ws://localhost:8000"
        except Exception as e:
            self._errors = f"Предупреждение: Ошибка при чтении IP. Использую http://localhost:8000"
            self.domen = "http://localhost:8000"
            self.ws_domen = "ws://localhost:8000"
        

    def save(self, path="config.json"):
        with open(path, 'w', encoding="utf-8") as file:
            json.dump(self.model_dump(), file, indent=2, ensure_ascii=False)

    def load(self, path="config.json"):
        path_obj = Path(path)
        if path_obj.exists() and path_obj.stat().st_size > 0:
            try:
                with open(path, 'r', encoding="utf-8") as file:
                    data = json.load(file)
                new_data = self.model_validate(data)
                self.username = new_data.username
                return self
            except (json.JSONDecodeError, Exception) as e:
                self.save(path)
                self._errors="Ошибка чтения конфига"
        else:
            self.save(path)
        return self
    
    def check_user(self):
        return self.username if self.username else ''
    
    
    
        