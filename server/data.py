from pydantic import BaseModel, ConfigDict
from typing import Annotated
from fastapi import WebSocket
import asyncio
from typing import Any
import json
import random
import os
import sys
import json
import random

def get_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, relative_path)

config_path = get_path(os.path.join("server", "config.json"))

try:
    with open(config_path, "r", encoding="utf-8") as f:
        _CONFIG = json.load(f)
except FileNotFoundError:
    alt_path = get_path("config.json")
    with open(alt_path, "r", encoding="utf-8") as f:
        _CONFIG = json.load(f)

QUESTIONS = _CONFIG.get("questions", [])
with open(config_path, "r", encoding="utf-8") as f:
    _CONFIG = json.load(f)

QUESTIONS = _CONFIG.get("questions", [])

def get_random_question():
    if not QUESTIONS:
        return None
    return random.choice(QUESTIONS)


class Lobby(BaseModel):
    usernames: dict[str, WebSocket] = {}
    max_players: int = 4 
    ready_users : list[int] = []
    users: list[str]=[]
    ready: bool = False
    money: dict[str,int] = {}
    balance: dict[str, int] = {}
    username_queue: dict[str,list[int]] = {}
    start: bool = True
    next_user: str = ""
    end_turn_users: list[str] = []
    property_owners: dict[int, str | None] = {} 
    auction: dict[str, Any] = None
    auction_queue: list = []
    auction_debt: dict | None = None
    eco_quest_current: dict[str, Any] | None = None   
    player_color: dict[str, int] = {}

    model_config = ConfigDict(arbitrary_types_allowed=True)

    DICT_STREET : dict[str, dict[int, int]]= {"brown" : {1:0,3:0}, "light_blue": {6:0,8:0,9:0}, "pink" : {11:0,13:0,14:0}, "orange" : {16:0, 18:0, 19:0}, "red" : {21:0,23:0,24:0}, "yellow" : {26:0,27:0,29:0}, "green": {31:0,32:0,34:0}, "blue": {37:0,39:0} }
    DICT_PAWN: dict[int, bool] = {1:False, 3: False, 6: False, 8: False, 9:False, 11: False, 13: False, 14: False, 16: False, 18: False, 19:False, 21:False, 23:False, 24: False, 26: False, 27:False, 29:False, 31 :False, 32:False, 34: False, 37:False, 39:False, 5:False,15:False, 25:False, 35:False, 12:False,28:False}
LOBBY_LISTS: set[str] = set()
DICT_LOBBY: dict[int, Lobby] = dict()
USERNAMES: set[str]  = set()

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


MORTGAGE_DATA = {
    1: 30,     # Казахская степь
    3: 30,     # Пампасы Аргентины
    5: 100,    # Северный морской путь
    6: 50,     # Река Нил
    8: 50,     # Река Янцзы
    9: 60,     # Река Ганг
    11: 70,    # Джунгли Борнео
    12: 75,    # Ветряная электростанция
    13: 70,    # Леса Конго
    14: 80,    # Леса Амазонии
    15: 100,   # Панамский канал
    16: 90,    # Ледники Гренландии
    18: 90,    # Льды Антарктиды
    19: 100,   # Арктический шельф
    21: 110,   # Индийский океан
    23: 110,   # Атлантический океан
    24: 120,   # Тихий океан
    25: 100,   # Транссибирская магистраль
    26: 130,   # Токио
    27: 130,   # Нью-Йорк
    28: 75,    # Опреснительная станция
    29: 140,   # Шанхай
    31: 150,   # Галапагосские острова
    32: 150,   # Озеро Байкал
    34: 160,   # Большой Барьерный риф
    35: 100,   # Суэцкий канал
    37: 175,   # Фукусимская зона
    39: 200    # Чернобыльская зона
}