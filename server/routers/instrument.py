from ..data import LOBBY_LISTS, Lobby
from fastapi import WebSocket
import random

STREETS_DATA = {
    "Казахская степь": {"price": 60},
    "Пампасы Аргентины": {"price": 60},
    "Река Нил": {"price": 100},
    "Река Янцзы": {"price": 100},
    "Река Ганг": {"price": 120},
    "Джунгли Борнео": {"price": 140},
    "Леса Конго": {"price": 140},
    "Леса Амазонии": {"price": 160},
    "Ледники Гренландии": {"price": 180},
    "Льды Антарктиды": {"price": 180},
    "Арктический шельф": {"price": 200},
    "Индийский океан": {"price": 220},
    "Атлантический океан": {"price": 220},
    "Тихий океан": {"price": 240},
    "Токио": {"price": 260},
    "Нью-Йорк": {"price": 260},
    "Шанхай": {"price": 280},
    "Озеро Байкал": {"price": 300},
    "Галапагосские острова": {"price": 300},
    "Большой Барьерный риф": {"price": 320},
    "Фукусимская зона": {"price": 350},
    "Чернобыльская зона": {"price": 400},
}

TRANSPORT_DATA = {
    "Северный морской путь": {"price": 200},
    "Панамский канал": {"price": 200},
    "Транссибирская магистраль": {"price": 200},
    "Суэцкий канал": {"price": 200},
}

UTILITY_DATA = {
    "Ветряная электростанция": {"price": 150},
    "Опреснительная станция": {"price": 150},
}


CELL_DATA = {
    0: "СТАРТ", 1: "Казахская степь", 2: "Эко-квест", 3: "Пампасы Аргентины", 4: "Эко-сбор",
    5: "Северный морской путь", 6: "Река Нил", 7: "Эко-квест", 8: "Река Янцзы", 9: "Река Ганг",
    10: "посетитель", 11: "Джунгли Борнео", 12: "Ветряная электростанция", 13: "Леса Конго", 14: "Леса Амазонии",
    15: "Панамский канал", 16: "Ледники Гренландии", 17: "Эко-квест", 18: "Льды Антарктиды", 19: "Арктический шельф",
    20: "Бесплатный отдых", 21: "Индийский океан", 22: "Эко-квест", 23: "Атлантический океан", 24: "Тихий океан",
    25: "Транссибирская магистраль", 26: "Токио", 27: "Нью-Йорк", 28: "Опреснительная станция", 29: "Шанхай",
    30: "На проверку", 31: "Галапагосские острова", 32: "Озеро Байкал", 33: "Эко-квест", 34: "Большой Барьерный риф",
    35: "Суэцкий канал", 36: "Эко-квест", 37: "Фукусимская зона", 38: "Налог на выбросы CO2", 39: "Чернобыльская зона"
}

def get_cell_price(cell_index: int) -> int:
    name = CELL_DATA.get(cell_index, "")
    if name in STREETS_DATA:
        return STREETS_DATA[name]["price"]
    if name in TRANSPORT_DATA:
        return TRANSPORT_DATA[name]["price"]
    if name in UTILITY_DATA:
        return UTILITY_DATA[name]["price"]
    return 0



def check_code(code: int) -> bool:
    if code in LOBBY_LISTS:
        return True
    return False


def generation_code_lobby() -> int:
    if len(LOBBY_LISTS) < 90_000:
        code = random.randint(10_000, 99_999)
        if check_code(code):
            code = generation_code_lobby()
        else: 
            LOBBY_LISTS.add(code)
        return code
    else:
        return 503


class ConnectionManager:
    def __init__(self, lobby: Lobby):
        self.lobby = lobby
        self.active_connections : dict[str, WebSocket] = lobby.usernames
    
    async def connect(self, username: str, websocket: WebSocket):
        self.active_connections[username] = websocket
        return self.active_connections
    
    def disconnect(self, username: str):
        if username in self.active_connections:
            self.active_connections.pop(username, None)
        return self.active_connections

    async def broadcast(self, message: dict):   
        for user in list(self.active_connections.keys()):
            connection = self.active_connections.get(user)
            if connection:
                try:
                    await connection.send_json(message)
                except Exception:
                    self.active_connections.pop(user, None)



def roll_dice():
    first_dice = random.randint(1,6)
    second_dice = random.randint(1,6)
    return [first_dice, second_dice]
            
    
def get_max(queue: dict[str, list[int]]):
    max_sum = 0
    max_user = None

    for user, numbers in queue.items():
        current_sum = sum(numbers)
        
        if current_sum > max_sum:
            max_sum = current_sum
            max_user = user

    return max_user


def get_ordered_list(queue: dict[str, list[int]], current_usernames: list[str]):
    starter = get_max(queue)
    start_idx = current_usernames.index(starter)
   
    return current_usernames[start_idx:] + current_usernames[:start_idx]

def roll_dice_unique(queue: dict[str, list[int]]):
    forbidden_sums = {sum(v) for v in queue.values()}

    result = roll_dice()

    while sum(result) in forbidden_sums:
        result = roll_dice()

    return result



    