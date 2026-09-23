import flet as ft
from data import Config
from websockets_orm import websocket
from utils import go_back
from alerts import AlertDialog_spawn
import asyncio

users_row: dict[str, ft.Container] = {}

TRANSPORT_DATA = {
    "Северный морской путь": {"price": 200, "mortgage": 100, "rent": [25, 50, 100, 200]},
    "Панамский канал": {"price": 200, "mortgage": 100, "rent": [25, 50, 100, 200]},
    "Транссибирская магистраль": {"price": 200, "mortgage": 100, "rent": [25, 50, 100, 200]},
    "Суэцкий канал": {"price": 200, "mortgage": 100, "rent": [25, 50, 100, 200]},
}

UTILITY_DATA = {
    "Ветряная электростанция": {"price": 150, "mortgage": 75, "multiplier": [4, 10]},
    "Опреснительная станция": {"price": 150, "mortgage": 75, "multiplier": [4, 10]},
}

TRANSPORT_INDICES = {5, 15, 25, 35}
UTILITY_INDICES = {12, 28}

CELL_COLORS = {
    # Коричневая группа (Казахская степь, Пампасы Аргентины)
    1: "#864C38", 3: "#864C38",

    # Светло-голубая группа (Река Нил, Река Янцзы, Река Ганг)
    6: "#ACDCF0", 8: "#ACDCF0", 9: "#ACDCF0",

    # Розово-малиновая группа (Джунгли Борнео, Леса Конго, Леса Амазонии)
    11: "#C53884", 13: "#C53884", 14: "#C53884",

    # Оранжевая группа (Ледники Гренландии, Льды Антарктиды, Арктический шельф)
    16: "#EC8B2C", 18: "#EC8B2C", 19: "#EC8B2C",

    # Красная группа (Индийский океан, Атлантический океан, Тихий океан)
    21: "#DB2428", 23: "#DB2428", 24: "#DB2428",

    # Жёлтая группа (Токио, Нью-Йорк, Шанхай)
    26: "#FFF004", 27: "#FFF004", 29: "#FFF004",

    # Зелёная группа (Галапагосские острова, Озеро Байкал, Большой Барьерный риф)
    31: "#13A857", 32: "#13A857", 34: "#13A857",

    # Синяя группа (Фукусимская зона, Чернобыльская зона)
    37: "#0066A4", 39: "#0066A4",
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

# Путь к логотипу экокоина
ECO_COIN_LOGO = "экокоин.png"

# Структура данных для улиц (цветных групп)
# Формат: "Название": [Цена_Покупки, Ур1, Ур2, Ур3, Ур4, Ур5]
STREETS_DATA = {
    # Коричневая группа
    "Казахская степь": {
        "price": 60,
        "rent": [2, 10, 30, 90, 160, 250],
        "star": 50
    },
    "Пампасы Аргентины": {
        "price": 60,
        "rent": [4, 20, 60, 180, 320, 450],
        "star": 50
    },

    # Голубая группа
    "Река Нил": {
        "price": 100,
        "rent": [6, 30, 90, 270, 400, 550],
        "star": 50
    },
    "Река Янцзы": {
        "price": 100,
        "rent": [6, 30, 90, 270, 400, 550],
        "star": 50
    },
    "Река Ганг": {
        "price": 120,
        "rent": [8, 40, 100, 300, 450, 600],
        "star": 50
    },

    # Розовая группа
    "Джунгли Борнео": {
        "price": 140,
        "rent": [10, 50, 150, 450, 625, 750],
        "star": 100
    },
    "Леса Конго": {
        "price": 140,
        "rent": [10, 50, 150, 450, 625, 750],
        "star": 100
    },
    "Леса Амазонии": {
        "price": 160,
        "rent": [12, 60, 180, 500, 700, 900],
        "star": 100
    },

    # Оранжевая группа
    "Ледники Гренландии": {
        "price": 180,
        "rent": [14, 70, 200, 550, 750, 950],
        "star": 100
    },
    "Льды Антарктиды": {
        "price": 180,
        "rent": [14, 70, 200, 550, 750, 950],
        "star": 100
    },
    "Арктический шельф": {
        "price": 200,
        "rent": [16, 80, 220, 600, 800, 1000],
        "star": 100
    },

    # Красная группа
    "Индийский океан": {
        "price": 220,
        "rent": [18, 90, 250, 700, 875, 1050],
        "star": 150
    },
    "Атлантический океан": {
        "price": 220,
        "rent": [18, 90, 250, 700, 875, 1050],
        "star": 150
    },
    "Тихий океан": {
        "price": 240,
        "rent": [20, 100, 300, 750, 925, 1100],
        "star": 150
    },

    # Жёлтая группа
    "Токио": {
        "price": 260,
        "rent": [22, 110, 330, 800, 975, 1150],
        "star": 150
    },
    "Нью-Йорк": {
        "price": 260,
        "rent": [22, 110, 330, 800, 975, 1150],
        "star": 150
    },
    "Шанхай": {
        "price": 280,
        "rent": [24, 120, 360, 850, 1025, 1200],
        "star": 150
    },

    # Зелёная группа
    "Озеро Байкал": {
        "price": 300,
        "rent": [26, 130, 390, 900, 1100, 1275],
        "star": 200
    },
    "Галапагосские острова": {
        "price": 300,
        "rent": [26, 130, 390, 900, 1100, 1275],
        "star": 200
    },
    "Большой Барьерный риф": {
        "price": 320,
        "rent": [28, 150, 450, 1000, 1200, 1400],
        "star": 200
    },

    # Синяя группа (дорогие)
    "Фукусимская зона": {
        "price": 350,
        "rent": [35, 175, 500, 1100, 1300, 1500],
        "star": 200
    },
    "Чернобыльская зона": {
        "price": 400,
        "rent": [50, 200, 600, 1400, 1700, 2000],
        "star": 200
    },
}



def get_card_info(street_name):
    data = STREETS_DATA.get(street_name)
    if not data:
        return None
    return {
        "название": street_name.upper(),
        "цена": data["price"],
        "rent": data["rent"],
        "star": data["star"]
    }

class BoardCell(ft.Container):
    def __init__(self, index: int, w: float, h: float, on_click_callback):
        super().__init__()
        self.index = index
        self.width = w
        self.height = h
        self.on_click = lambda _: on_click_callback(self.index)
        self.bgcolor = "#00FFFFFF" 
        self.players_container = ft.Stack()
        self.buildings_layer = ft.Stack()
        self.content = ft.Stack([
            self.buildings_layer,
            self.players_container
        ])           

    def add_token(self, token: ft.Container, in_jail: bool = False):
        # Считаем текущее количество по категориям
        jail_tokens = [c for c in self.players_container.controls if getattr(c, "is_jail", False)]
        visitor_tokens = [c for c in self.players_container.controls if not getattr(c, "is_jail", False)]
        
        t_size = 22  # Размер фишки как на скрине
        
        if self.index == 10:
            padding = 8
            inner_w = self.width - padding * 2
            inner_h = self.height - padding * 2

            t_size = 22
            gap = 4

            # --- ЗАКЛЮЧЕННЫЕ (центр 2x2) ---
            if in_jail:
                idx = len(jail_tokens) % 4

                t_size = 22
                gap = 4

                # 🔥 РАЗМЕР ОРАНЖЕВОГО КВАДРАТА (подгони если надо)
                jail_size = min(self.width, self.height) * 0.45

                # 🔥 СМЕЩЕНИЕ ВНУТРЬ (это ключ!)
                jail_offset_x = self.width * 0.4
                jail_offset_y = self.height * 0.14

                grid = [
                    (0, 0), (0, 1),
                    (1, 0), (1, 1)
                ]

                row, col = grid[idx]

                total_w = t_size * 2 + gap
                total_h = t_size * 2 + gap

                # центр внутри ОРАНЖЕВОГО блока
                start_x = jail_offset_x + (jail_size - total_w) / 2
                start_y = jail_offset_y + (jail_size - total_h) / 2

                left = start_x + col * (t_size + gap)
                top = start_y + row * (t_size + gap)

                is_jail_flag = True

            # --- ПОСЕТИТЕЛИ (по краям Г-образно) ---
            else:
                idx = len(visitor_tokens) % 4

                t_size = 22
                gap = 4

                left = 0
                top = 0

                if idx == 0:
                    left = self.width * 0.05
                    top = self.height * 0.3

                elif idx == 1:
                    left = self.width * 0.05
                    top = self.height * 0.6

                elif idx == 2:
                    left = self.width * 0.35
                    top = self.height * 0.75

                elif idx == 3:
                    left = self.width * 0.65
                    top = self.height * 0.75

                is_jail_flag = False
        else:
            # --- ВСЕ ОСТАЛЬНЫЕ КЛЕТКИ ---
            idx = len(self.players_container.controls) % 4
            # Центрированная сетка 2x2
            gap = 5
            grid = [
                {"t": 0, "l": 0}, {"t": 0, "l": t_size + gap},
                {"t": t_size + gap, "l": 0}, {"t": t_size + gap, "l": t_size + gap}
            ]
            
            # Базовый центр
            center_x = (self.width - (t_size * 2 + gap)) / 2
            center_y = (self.height - (t_size * 2 + gap)) / 2
            
            # Сдвиг от цветных полос (как на нижних полях)
            if 0 < self.index < 10:    center_y += 15 # Низ
            elif 11 <= self.index <= 19: center_x -= 15 # Лево
            elif 21 <= self.index <= 29: center_y -= 15 # Верх
            elif 31 <= self.index <= 39: center_x += 15 # Право

            top = center_y + grid[idx]["t"]
            left = center_x + grid[idx]["l"]
            is_jail_flag = False

        # Создаем финальный контейнер
        wrapper = ft.Container(
            content=token,
            width=t_size,
            height=t_size,
            top=top,
            left=left
        )
        wrapper.is_jail = is_jail_flag # Помечаем для корректного счета
        self.players_container.controls.append(wrapper)

    def remove_token(self, token: ft.Container):
        for ctrl in self.players_container.controls[:]:
            if isinstance(ctrl, ft.Container) and ctrl.content == token:
                self.players_container.controls.remove(ctrl)
                break


class GameView(ft.View):
    def __init__(self, config: Config, height):
        super().__init__(route="/game", padding=0)
        # === АУКЦИОН: инициализация переменных ===
        self._auction_history: list = []           # [(username, bid), ...]
        self._auction_time_left: int = 5           # секунды до завершения
        self._auction_timer_task: asyncio.Task | None = None
        self._auction_timer_text: ft.Text | None = None
        self._auction_timer_bar: ft.ProgressBar | None = None
        self._auction_history_column: ft.Column | None = None
        self._auction_state: dict = {}       
        self.player_border_color = {}
        self.player_fill_color = {}
        self.is_rolling_phase = True  # сначала жеребьёвка
        self.property_owners = {}          # {индекс_клетки: владелец или None}
        self.property_levels = {}
        self._upgrade_mode = False
        self._upgrade_cells = []
        self.pawned_cells = set()
        self._pawn_mode = False
        self._pawn_cells = []
        self._redeem_cells = []
        self._pawn_pending = False
        self._sell_mode = False
        self._sell_cells = []
        self._sell_pending = False
        self._payment_mode = False
        self._payment_amount = 0
        self._payment_selection = None
        self._upgrade_pending = False
        self.pending_purchase_cell = None
        self.height_ = height
        self.config = config
        self.player_color_map = getattr(config, "player_color", {}) or {}
        self.expand = True
        self.bgcolor = "#F5EAD4"
        self.vertical_alignment = ft.MainAxisAlignment.CENTER
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.cells_objects: dict[int, ft.Container] = {}
        self._auction_overlay = None      # Текущий оверлей аукциона
        self._auction_initiator = None    # Кто начал аукцион
        self._auction_bid_text = None     # Ссылка на текст текущей ставки
        self._auction_leader_text = None  # Ссылка на текст лидера
        self._auction_big_btn = None      # Кнопка BIG BID
        self._auction_small_btn = None    # Кнопка BID
        self._auction_current_bid = 0     # Текущая ставка
        self._auction_cell_index = None
        self._auction_queue = []
        self._left_players = set()
        self.display_order = list(self.config.usernames)
        self._auction_overlay = None
        self._auction_state = {}
        self._auction_timer_task = None
        self._auction_time_left = 5

        self._eco_selected_index = None           # запоминаем выбранный вариант
        self._eco_answer_sent = False
        self._eco_quest_overlay = None   # оверлей вопроса эко-квеста

        self._auction_bid_text = None
        self._auction_leader_text = None
        self._auction_timer_text = None

        self._auction_left_btn = None
        self._auction_right_btn = None
        self._auction_left_btn_text = None
        self._auction_right_btn_text = None

        self.card_layer = ft.Container(
            content=None,
            visible=False,
            expand=True,
            bgcolor="#88000000", # затемнение фона
            alignment=ft.Alignment.CENTER,
        )

        board_size = self.height_ - 20
        # --- РАСЧЕТ ГЕОМЕТРИИ ---
        # Коэффициент: угол в 1.6 раза шире обычной клетки
        corner_coef = 1.6 
        # Вычисляем базовую ширину обычной клетки
        self.std_w = board_size / (9 + 2 * corner_coef)
        self.corner_w = self.std_w * corner_coef
        self.player_positions = {} 
        self.player_tokens = {}
        self.player_balances = {name: 0 for name in self.config.usernames}
        self.player_balance = {name: 0 for name in self.config.usernames}
        # Генерируем невидимые кнопки поверх фона
        self.grid_overlay = ft.Container(
            content=ft.Stack(
            controls=[],
            width=board_size,
            height=board_size,
            ),
            alignment=ft.Alignment.CENTER,
        )
        self.build_grid_zones(board_size)
                
        for i, name in enumerate(self.config.usernames):
            style = self._player_style(name, i)
            self.player_fill_color[name] = style["color"]
            self.player_border_color[name] = style["border"]
            token = ft.Container(
                content=ft.Container(
                    bgcolor=style["color"],
                    shape=ft.BoxShape.CIRCLE,
                    margin=2, # Добавили отступ, чтобы фишка была с "дыркой" внутри обводки
                ),
                width=20, # Размер 20, как в списке
                height=20,
                shape=ft.BoxShape.CIRCLE,
                border=ft.Border.all(2.5, style["border"]), # Обводка 2.5
                animate=ft.Animation(300, ft.AnimationCurve.DECELERATE)
            )
            self.player_border_color[name] = style["border"]
            self.player_tokens[name] = token
            self.player_positions[name] = 0
            self.cells_objects[0].add_token(token)


        self.info_container = ft.Container(
            top=40,
            right=10,
            width=320, 
            content=ft.Column(
                controls=[self.build_player_row(i, name) for i, name in enumerate(self.config.usernames)],
                tight=True,
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH, 
            ),
        )
        self.roll_button = ft.Container(
            visible=False,
            
            content=ft.Button(
                on_click=self.roll_button_dice_action,
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CASINO, color="white", size=20),
                        ft.Text("БРОСИТЬ КУБИК", size=14, weight=ft.FontWeight.BOLD, color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True,
                ),
                style=ft.ButtonStyle(
                    bgcolor={"": "#234746", ft.ControlState.HOVERED: "#1b3837"},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                ),
                
            ),
            alignment=ft.Alignment.CENTER,
        )

        self.end_turn_button = ft.Container(
            visible=False, # По умолчанию скрыта
            content=ft.Button(
                on_click=self.end_turn_action, # Нужно будет создать этот метод
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.DONE_ALL, color="white", size=20),
                        ft.Text("ЗАКОНЧИТЬ ХОД", size=14, weight=ft.FontWeight.BOLD, color="white"),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    tight=True,
                ),
                style=ft.ButtonStyle(
                    bgcolor={"": "#234746", ft.ControlState.HOVERED: "#1b3837"},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                ),
            ),
        )
        self.upgrade_button = ft.Button(
            on_click=self.upgrade_action,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.ECO, color="white", size=18),
                    ft.Text("УЛУЧШИТЬ", size=14, weight=ft.FontWeight.BOLD, color="white"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            style=ft.ButtonStyle(
                bgcolor={"": "#2E7D32", ft.ControlState.HOVERED: "#1B5E20"},
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            ),
        )
        self.upgrade_wrap = ft.Container(content=self.upgrade_button, visible=False, bottom=185, right=20)
        self.pawn_button = ft.Button(
            on_click=self.pawn_action,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.GAVEL, color="white", size=18),
                    ft.Text("ЗАЛОЖИТЬ", size=14, weight=ft.FontWeight.BOLD, color="white"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            style=ft.ButtonStyle(
                bgcolor={"": "#E65100", ft.ControlState.HOVERED: "#BF360C"},
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            ),
        )
        self.pawn_wrap = ft.Container(content=self.pawn_button, visible=False, bottom=95, right=20)
        self.sell_button = ft.Button(
            on_click=self.sell_action,
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.REMOVE_CIRCLE_OUTLINE, color="white", size=18),
                    ft.Text("СНЯТЬ УРОВЕНЬ", size=14, weight=ft.FontWeight.BOLD, color="white"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                tight=True,
            ),
            style=ft.ButtonStyle(
                bgcolor={"": "#E65100", ft.ControlState.HOVERED: "#BF360C"},
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            ),
        )
        self.sell_wrap = ft.Container(content=self.sell_button, visible=False, bottom=140, right=20)
        # Контейнер для анимации кубиков
        self.dice_display = ft.Container(
            content=ft.Row(
                [
                    ft.Container( # Первый кубик
                        content=ft.Text("?", size=40, weight="bold", color="#234746"),
                        width=80, height=80,
                        bgcolor="white",
                        border_radius=15,
                        alignment=ft.Alignment.CENTER,
                        border=ft.Border.all(4, "transparent") # Обводка меняется динамически
                    ),
                    ft.Container( # Второй кубик
                        content=ft.Text("?", size=40, weight="bold", color="#234746"),
                        width=80, height=80,
                        bgcolor="white",
                        border_radius=15,
                        alignment=ft.Alignment.CENTER,
                        border=ft.Border.all(4, "transparent")
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
            visible=False, # Скрыт, пока не бросят
            alignment=ft.Alignment.CENTER,
        )
        asyncio.create_task(self.spawn_players())
        self.rolling_banner = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.CASINO, color="white", size=22),
                    ft.Text("ЖЕРЕБЬЁВКА", size=20, weight=ft.FontWeight.W_900, color="white"),
                    ft.Icon(ft.Icons.HOURGLASS_TOP, color="#FFE082", size=20),
                ],
                spacing=12,
                tight=True,
            ),
            bgcolor="#234746",
            border_radius=30,
            padding=ft.Padding.symmetric(horizontal=24, vertical=12),
            shadow=ft.BoxShadow(blur_radius=12, color="#55000000"),
            visible=True,
        )

        self.controls = [
            ft.Stack(
                [
                    # 1. Игровое поле (Самый нижний слой)
                    ft.Container(
                        content=ft.Container(
                            image=ft.DecorationImage(
                                src=r"..\assets\Игровое поле2.png",
                                fit=ft.BoxFit.CONTAIN,
                            ),
                            width=board_size,
                            height=board_size,
                        ),
                        alignment=ft.Alignment.CENTER,
                        expand=True,
                    ),
                    self.grid_overlay,

                    # 2. Кнопка назад (Позиционируем в угол)
                    ft.Container(
                        left=20,
                        top=20,
                        content=ft.IconButton(
                            icon=ft.Icons.ARROW_BACK_OUTLINED,
                            on_click=self.go_back,
                            icon_size=30,
                            icon_color="#234746"
                        ),
                    ),

                    # 3. Информационный контейнер (Справа)
                    # Убедитесь, что внутри self.info_container НЕ задан expand=True
                    self.info_container,

                    # 4. Кнопка БРОСИТЬ КУБИК
                    ft.Container(
                        content=self.roll_button,
                        bottom=150,
                        left=0,
                        right=0,   
                    ),

                    # 5. Кнопка ЗАКОНЧИТЬ ХОД
                    ft.Container(
                        content=self.end_turn_button,
                        bottom=40,
                        right=20,
                    ),
                    self.upgrade_wrap,
                    self.pawn_wrap,
                    self.sell_wrap,
                    self.dice_display,
                    ft.Container(
                        content=self.rolling_banner,
                        top=150,
                        left=0,
                        right=0,
                        alignment=ft.Alignment.CENTER,
                    ),
                    self.card_layer
                ],
                expand=True,
            ),
        ]
        self._end_turn_wrap = self.controls[0].controls[5]
    #     asyncio.create_task(
    #     self.show_rent_animation(
    #         payer=self.config.username,
    #         receiver=self.config.usernames[0],
    #         amount=100,
    #         cell_name="ТЕСТ КЛЕТКА"
    #     )
    # )

    def did_mount(self):
        self.page.on_resize = lambda e: self._place_info()
        self._place_info()

    def _place_info(self):
        w = self.page.width
        h = self.page.height
        board_size = h - 20
        board_right = (w + board_size) / 2
        delta = (w - board_size) / 2 - 301.6
        self.info_container.width = None
        self.info_container.left = board_right
        self.info_container.right = 10
        for c in self.controls[0].controls:
            if getattr(c, 'content', None) is self.end_turn_button:
                c.right = max(5, 20 + delta)
            if getattr(c, 'content', None) is self.roll_button:
                c.bottom = 10 + board_size * 0.2115
            if getattr(c, 'content', None) is self.upgrade_button:
                c.right = max(5, 20 + delta)
            if getattr(c, 'content', None) is self.pawn_button:
                c.right = max(5, 20 + delta)
            if getattr(c, 'content', None) is self.sell_button:
                c.right = max(5, 20 + delta)
                if getattr(c, 'content', None) is self.rolling_banner:
                    c.top = 30 + board_size * 0.131
        self.info_container.update()

    def _player_style(self, username, fallback_index=0):
        default_styles = [
            {"color": "#2A36B1", "border": "#0099FF"},
            {"color": "#9F0000", "border": "#FF0000"},
            {"color": "#38B000", "border": "#70E000"},
            {"color": "#9A8C00", "border": "#FFD700"},
        ]
        fallback = default_styles[fallback_index % len(default_styles)]
        value = getattr(self, "player_color_map", {}).get(username)
        if isinstance(value, dict):
            fill = value.get("color") or value.get("fill") or value.get("bgcolor")
            border = value.get("border") or value.get("border_color")
            if fill or border:
                return {"color": fill or fallback["color"], "border": border or fallback["border"]}
        elif isinstance(value, (list, tuple)) and len(value) >= 2:
            return {"color": value[0], "border": value[1]}
        elif isinstance(value, str):
            return {"color": value, "border": value}
        return {
            "color": self.player_fill_color.get(username, fallback["color"]),
            "border": self.player_border_color.get(username, fallback["border"]),
        }

    def set_player_colors(self, player_color):
        if not isinstance(player_color, dict):
            return
        self.player_color_map = player_color.copy()
        for i, name in enumerate(self.config.usernames):
            style = self._player_style(name, i)
            self.player_fill_color[name] = style["color"]
            self.player_border_color[name] = style["border"]
            token = self.player_tokens.get(name)
            if token is not None:
                token.border = ft.Border.all(2.5, style["border"])
                if getattr(token, "content", None) is not None:
                    token.content.bgcolor = style["color"]
                token.update()
            indicator = users_row.get(name)
            if indicator is not None:
                indicator.border = ft.Border.all(2.5, style["border"])
                if getattr(indicator, "content", None) is not None:
                    indicator.content.bgcolor = style["color"]
                indicator.update()

    def build_player_row(self, index, username):
        style = self._player_style(username, index)
        self.player_fill_color[username] = style["color"]
        self.player_border_color[username] = style["border"]
        try:
            player_balance = self.player_balances.get(username, 0)
        except (IndexError, TypeError):
            player_balance = 0

        indicator = ft.Container(
            content=ft.Container(
                bgcolor=style["color"],
                shape=ft.BoxShape.CIRCLE,
                margin=2,
            ),
            width=20, height=20, shape=ft.BoxShape.CIRCLE,
            border=ft.Border.all(2.5, style["border"]),
        )
        users_row[username] = indicator

        return ft.Container(
            content=ft.Row(
                [
                    ft.Row(
                        [
                            indicator,
                            ft.Container(
                                content=ft.Text(username, size=16, weight=ft.FontWeight.W_700, color="#234746"),
                                width=170,
                            ),
                        ],
                        spacing=10, tight=True,
                    ),
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Image(src=r"..\assets\экокоин.png", width=22, height=22),
                                ft.Text(f"{player_balance}", size=18, weight=ft.FontWeight.W_900, color="#1B5E20"),
                            ],
                            spacing=5, tight=True,
                        ),
                        alignment=ft.Alignment.CENTER_RIGHT, expand=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=ft.Padding.only(left=5, right=10),
        )
    
    async def go_back(self, e=None):
        # Закрываем сокет
        await websocket.close(self.config)
        # Переходим назад (убедись, что твоя функция из utils это умеет)
        from utils import go_back as global_go_back
        await global_go_back(e, self.config)
        

    async def roll_button_dice_action(self, e):
        websocket.send_action('dice', username=self.config.username)
        self.roll_button.visible = False
        self.update()

    async def update_roll_dice_button(self, data: dict):
        current_turn_username = data.get("username_roll")

        if current_turn_username == self.config.username:
            self.roll_button.visible = True
            self.end_turn_button.visible = False 
        else:
            self.roll_button.visible = False
            self.end_turn_button.visible = False

        self.update()

    async def end_turn_action(self, e):
        websocket.send_action('end_turn', username=self.config.username)
        self.end_turn_button.visible = False
        self.update()

    async def roll_dice_container(self, username: str, dice: list[int]):
        import random
        import asyncio

        player_styles = [
            {"color": "#2A36B1", "border": "#0099FF"},
            {"color": "#9F0000", "border": "#FF0000"},
            {"color": "#38B000", "border": "#70E000"},
            {"color": "#9A8C00", "border": "#FFD700"},
        ]

        try:
            p_idx = self.config.usernames.index(username)
            stroke_color = self.player_border_color.get(username, "#234746")
        except (ValueError, IndexError):
            stroke_color = "#234746"

        dice_row = self.dice_display.content.controls
        for d_cont in dice_row:
            d_cont.border = ft.Border.all(5, stroke_color)

        self.dice_display.visible = True
        self.dice_display.update()

        # Анимация
        for _ in range(12):
            dice_row[0].content.value = str(random.randint(1, 6))
            dice_row[1].content.value = str(random.randint(1, 6))
            self.dice_display.update()
            await asyncio.sleep(0.05)

        # Финальные значения
        dice_row[0].content.value = str(dice[0])
        dice_row[1].content.value = str(dice[1])
        self.dice_display.update()

        # ✅ Сразу скрываем кубики (ещё до движения)
        await asyncio.sleep(1)  # небольшая пауза, чтобы игрок увидел результат
        self.dice_display.visible = False
        self.dice_display.update()

        # Теперь движение (и возможное открытие диалога)
        if not self.is_rolling_phase:
            total_steps = sum(dice)
            await self.move_player(username, total_steps)

            

        # Жеребьёвка: показываем кнопку завершения хода
        if self.is_rolling_phase:
            if self.config.username == username:
                self.end_turn_button.visible = True
                self.end_turn_button.update()
            else:
                self.end_turn_button.visible = False
                self.end_turn_button.update()
        # В обычной игре кнопка появится после check_and_offer_purchase
    async def go_back_def(self, e):
            await websocket.close(self.config)
            await go_back(e, self.config)

    async def winner(self, data: dict):
        """Показывает финальную карточку победы всем игрокам после события win."""
        # Не показываем карточку повторно, если сервер прислал win больше одного раза.
        if getattr(self, "_win_overlay", None) is not None:
            return

        winner = data.get("username", "")
        if isinstance(winner, (set, list, tuple)):
            winner = next(iter(winner), "") if winner else ""
        winner = str(winner)

        is_me = winner == self.config.username

        # После окончания игры блокируем обычные действия.
        self.roll_button.visible = False
        self.end_turn_button.visible = False
        self.upgrade_wrap.visible = False
        self.pawn_wrap.visible = False
        self.sell_wrap.visible = False

        title = "ПОБЕДА!" if is_me else "ИГРА ОКОНЧЕНА"
        subtitle = "Вы победили!" if is_me else "Победитель:"
        border_color = self.player_border_color.get(winner, "#234746")

        winner_card = ft.Container(
            width=460,
            bgcolor="white",
            border_radius=18,
            border=ft.Border.all(4, border_color),
            padding=ft.Padding.all(32),
            shadow=ft.BoxShadow(blur_radius=24, color="#55000000"),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=14,
                controls=[
                    ft.Icon(
                        ft.Icons.EMOJI_EVENTS,
                        size=64,
                        color=border_color,
                    ),
                    ft.Text(
                        title,
                        size=30,
                        weight=ft.FontWeight.W_900,
                        color=border_color,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        subtitle,
                        size=17,
                        color="#666666",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        winner,
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color="#234746",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=8),
                    ft.Button(
                        content=ft.Text(
                            "В ЛОББИ",
                            color="white",
                            weight=ft.FontWeight.BOLD,
                        ),
                        on_click=self.go_back,
                        style=ft.ButtonStyle(
                            bgcolor={"": "#234746", ft.ControlState.HOVERED: "#1B3837"},
                            shape=ft.RoundedRectangleBorder(radius=10),
                            padding=ft.Padding.symmetric(
                                horizontal=28,
                                vertical=12,
                            ),
                        ),
                    ),
                ],
            ),
        )

        self._win_overlay = ft.Container(
            content=winner_card,
            expand=True,
            bgcolor="#AA000000",
            alignment=ft.Alignment.CENTER,
        )

        main_stack = self.controls[0]
        main_stack.controls.append(self._win_overlay)

        self.update()
        if self.page:
            self.page.update()

    async def close(self):
        if self.page:
            alert = AlertDialog_spawn("Лобби удалено", text_button="Ок", my_page=self.page, on_click=self.go_back_def)
            alert.alert_spawn(self.config)

    async def update_players_list(self, usernames=None):
        if usernames is not None:
            # Обновляем config.usernames (порядок хода), но НЕ трогаем display_order
            self.config.usernames = usernames
            for i, name in enumerate(usernames):
                style = self._player_style(name, i)
                self.player_fill_color[name] = style["color"]
                self.player_border_color[name] = style["border"]

            # Добавляем баланс новым игрокам (если вдруг появились)
            for name in usernames:
                if name not in self.player_balances:
                    self.player_balances[name] = 0

            self.config.money = {name: self.player_balances[name] for name in usernames}

        # НЕ пересоздаём строки — обновляем ТОЛЬКО цифры баланса
        self.update_balance_display()
        self.apply_ownership_visuals()
        self.update_pawn_visuals()
        if not self.is_rolling_phase:
            self.rolling_banner.visible = False

        self.update()
        if self.page:
            self.page.update()

    def build_grid_zones(self, board_size):
        """Размещение 40 кликабельных зон по периметру 11x11"""
        # Сбрасываем старые контроли
        self.grid_overlay.content.controls.clear()
        
        # Коэффициент 1.6 обычно хорошо подходит под классическую разметку, 
        # где угол — это квадрат, а улица — прямоугольник.
        corner_coef = 1.6 
        std_w = board_size / (9 + 2 * corner_coef)
        corner_w = std_w * corner_coef

        for i in range(40):
            is_corner = i % 10 == 0
            
            # 1. ОПРЕДЕЛЕНИЕ ГЕОМЕТРИИ (Ширина и Высота)
            if is_corner:
                w, h = corner_w, corner_w
            elif (0 < i < 10) or (20 < i < 30):
                # Горизонтальные стороны (Нижняя и Верхняя)
                w, h = std_w, corner_w
            else:
                # Вертикальные стороны (Левая и Правая)
                w, h = corner_w, std_w

            # Создаем ячейку (пока с HEX-обводкой для теста)
            cell = BoardCell(i, w, h, self.show_cell_info)
            
            # РАСКОММЕНТИРУЙ ДЛЯ ОТЛАДКИ (чтобы видеть сетку):
            # cell.border = ft.Border.all(1, "#44000000") 

            # 2. ТОЧНОЕ ПОЗИЦИОНИРОВАНИЕ (Координаты в Stack)
            # НИЖНЯЯ СТОРОНА (0 -> 10, Справа налево)
            if 0 <= i <= 10:
                cell.bottom = 0
                if i == 0: 
                    cell.right = 0
                elif i == 10:
                    cell.left = 0
                else:
                    cell.right = corner_w + (i - 1) * std_w

            # ЛЕВАЯ СТОРОНА (11 -> 20, Снизу вверх)
            elif 11 <= i <= 20:
                cell.left = 0
                if i == 20:
                    cell.top = 0
                else:
                    cell.bottom = corner_w + (i - 11) * std_w

            # ВЕРХНЯЯ СТОРОНА (21 -> 30, Слева направо)
            elif 21 <= i <= 30:
                cell.top = 0
                if i == 30:
                    cell.right = 0
                else:
                    cell.left = corner_w + (i - 21) * std_w

            # ПРАВАЯ СТОРОНА (31 -> 39, Сверху вниз)
            elif 31 <= i <= 39:
                cell.right = 0
                cell.top = corner_w + (i - 31) * std_w

            self.cells_objects[i] = cell
            self.grid_overlay.content.controls.append(cell)


    async def spawn_players(self):
        # очистим все клетки
        for cell in self.cells_objects.values():
            cell.players_container.controls.clear()

        # создаём игроков
        for i, name in enumerate(self.config.usernames):
            style = self._player_style(name, i)
            self.player_fill_color[name] = style["color"]
            self.player_border_color[name] = style["border"]

            token = ft.Container(
                content=ft.Container(
                    bgcolor=style["color"],
                    shape=ft.BoxShape.CIRCLE,
                    margin=2,
                ),
                width=20,
                height=20,
                shape=ft.BoxShape.CIRCLE,
                border=ft.Border.all(2.5, style["border"]),
                animate=ft.Animation(300, ft.AnimationCurve.DECELERATE)
            )

            self.player_tokens[name] = token
            self.player_positions[name] = 0

            # ставим ВСЕХ на старт
            self.cells_objects[0].add_token(token)

        self.cells_objects[0].update()

        if self.page:
            self.page.update()


    async def remove_money(self, username: str, num: int, cell_name: str = ""):
        stroke_color = self.player_border_color.get(username, "#234746")

        card = ft.Container(
            width=550,
            bgcolor="white",
            border_radius=16,
            border=ft.Border.all(5, stroke_color),
            padding=ft.Padding.all(30),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color="#44000000",
            ),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text(cell_name.upper() if cell_name else "ОПЛАТА", size=14, weight=ft.FontWeight.BOLD, color="#999999", text_align=ft.TextAlign.CENTER),
                    ft.Text(username, size=22, weight=ft.FontWeight.BOLD, color="#234746", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Text(f"−{num}", size=32, weight=ft.FontWeight.BOLD, color="#D32F2F"),
                            ft.Image(src=ECO_COIN_LOGO, width=30, height=30, fit=ft.BoxFit.CONTAIN),
                        ]
                    )
                ]
            )
        )

        overlay = ft.Container(
            content=card,
            expand=True,
            bgcolor="#88000000",
            alignment=ft.Alignment.CENTER,
        )

        main_stack = self.controls[0]
        main_stack.controls.append(overlay)
        self.update()
        if self.page:
            self.page.update()

        await asyncio.sleep(4)

        if overlay in main_stack.controls:
            main_stack.controls.remove(overlay)
        self.update()
        if self.page:
            self.page.update()


    async def add_200(self, username: str):
        if username == self.config.username:
            websocket.send_action("add_200", username=username)

        card = ft.Container(
            width=550,
            bgcolor="white",
            border_radius=16,
            border=ft.Border.all(3, "#2E7D32"),
            padding=ft.Padding.all(30),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color="#44000000",
            ),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("ПРОХОД ЧЕРЕЗ СТАРТ", size=14, weight=ft.FontWeight.BOLD, color="#999999", text_align=ft.TextAlign.CENTER),
                    ft.Text(username, size=22, weight=ft.FontWeight.BOLD, color="#234746", text_align=ft.TextAlign.CENTER),
                    ft.Container(height=20),
                    ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=6,
                        controls=[
                            ft.Text("+200", size=32, weight=ft.FontWeight.BOLD, color="#2E7D32"),
                            ft.Image(src=ECO_COIN_LOGO, width=30, height=30, fit=ft.BoxFit.CONTAIN),
                        ]
                    )
                ]
            )
        )

        overlay = ft.Container(
            content=card,
            expand=True,
            bgcolor="#88000000",
            alignment=ft.Alignment.CENTER,
        )

        main_stack = self.controls[0]
        main_stack.controls.append(overlay)
        self.update()
        if self.page:
            self.page.update()

        await asyncio.sleep(3)

        if overlay in main_stack.controls:
            main_stack.controls.remove(overlay)
        self.update()
        if self.page:
            self.page.update()

    async def move_player(self, username: str, steps: int, force_jail: bool = False):
        token = self.player_tokens.get(username)
        if not token:
            return

        new_idx = self.player_positions.get(username, 0)

        for _ in range(steps):
            old_idx = new_idx
            new_idx = (old_idx + 1) % 40
            self.cells_objects[old_idx].remove_token(token)
            self.player_positions[username] = new_idx

            if new_idx == 10:
                self.cells_objects[new_idx].add_token(token, in_jail=force_jail)
            else:
                self.cells_objects[new_idx].add_token(token)

            self.cells_objects[old_idx].update()
            self.cells_objects[new_idx].update()

            if self.page:
                self.page.update()

            if new_idx == 0:
                await self.add_200(username)
            else: 
                await asyncio.sleep(0.08)
        print("Ход прошел")
        # НЕ вызываем update_players_list здесь — позиции не связаны с балансами
        self.apply_ownership_visuals()

        if not self.is_rolling_phase:
            await self.check_and_offer_purchase(username, new_idx)


    def _build_rent_row(self, label, value, is_bold=False, is_small=False, use_logo=True):
        font_size = 14 if not is_small else 12
        weight = ft.FontWeight.BOLD if is_bold else ft.FontWeight.NORMAL

        right = ft.Row(
            [
                ft.Text(str(value), size=font_size, weight=ft.FontWeight.BOLD, color="#234746"),
            ],
            spacing=5,
            tight=True
        )

        if use_logo:
            right.controls.append(
                ft.Image(
                    src=ECO_COIN_LOGO,
                    width=font_size + 2,
                    height=font_size + 2,
                    fit="contain"
                )
            )

        return ft.Container(
            padding=ft.Padding.symmetric(horizontal=10, vertical=2),
            content=ft.Row(
                [
                    ft.Text(label, size=font_size, weight=weight, color="#234746"),
                    right
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            )
        )
    
    def show_cell_info(self, index, purchase_mode=False):
        if getattr(self, "_payment_mode", False):
            if self._payment_selection == "pawn":
                self.try_pawn_cell(index)
            elif self._payment_selection == "sell":
                self.try_sell_cell(index)
            return
        if self._upgrade_mode:
            self.try_upgrade_cell(index)
            return
        if self._pawn_mode:
            self.try_pawn_cell(index)
            return
        if self._sell_mode:
            self.try_sell_cell(index)
            return
        cell_name = CELL_DATA.get(index)

        # ========== ТРАНСПОРТ ==========
        if index in TRANSPORT_INDICES:
            data = TRANSPORT_DATA.get(cell_name)
            if not data:
                return
            rent = data["rent"]
            card_content = ft.Column(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.DIRECTIONS_BOAT, size=36, color="white"),
                            ft.Text(cell_name.upper(), size=14, weight="bold", color="white",
                                    text_align=ft.TextAlign.CENTER),
                        ], alignment=ft.MainAxisAlignment.CENTER,
                           horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        bgcolor="#444444", padding=ft.Padding.all(10), width=280,
                        border=ft.Border.all(2, "black"),
                    ),
                    ft.Container(height=10),
                    self._build_rent_row("1 транспортная компания", rent[0]),
                    self._build_rent_row("2 транспортные компании", rent[1]),
                    self._build_rent_row("3 транспортные компании", rent[2]),
                    self._build_rent_row("4 транспортные компании", rent[3], is_bold=True),
                    ft.Divider(height=20, thickness=2, color="black"),
                    self._build_rent_row("Стоимость покупки", data["price"], is_small=True),
                    self._build_rent_row("Залоговая стоимость", data["mortgage"], is_small=True),
                    self._build_card_buttons(index, purchase_mode, cell_name, data["price"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, tight=True,
            )
            self.card_layer.content = ft.Container(
                content=ft.Container(width=300, padding=10, bgcolor="white",
                    border_radius=10, border=ft.Border.all(2, "black"),
                    content=card_content),
                alignment=ft.Alignment.CENTER, expand=True,
            )
            self.card_layer.visible = True
            self.update()
            return

        # ========== КОММУНАЛКА ==========
        if index in UTILITY_INDICES:
            data = UTILITY_DATA.get(cell_name)
            if not data:
                return
            mult = data["multiplier"]
            card_content = ft.Column(
                [
                    ft.Container(
                        content=ft.Column([
                            ft.Icon(ft.Icons.WIND_POWER if "Ветряная" in cell_name else ft.Icons.WATER_DROP,
                                    size=36, color="white"),
                            ft.Text(cell_name.upper(), size=14, weight="bold", color="white",
                                    text_align=ft.TextAlign.CENTER),
                        ], alignment=ft.MainAxisAlignment.CENTER,
                           horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=4),
                        bgcolor="#2E7D32", padding=ft.Padding.all(10), width=280,
                        border=ft.Border.all(2, "black"),
                    ),
                    ft.Container(height=10),
                    ft.Container(
                        content=ft.Text(
                            "Если у вас ОДНО предприятие —\nрента = сумма кубиков × множитель",
                            size=12, color="#234746", text_align=ft.TextAlign.CENTER),
                        padding=ft.Padding.symmetric(horizontal=10),
                    ),
                    ft.Container(height=5),
                    self._build_rent_row("1 предприятие", f"×{mult[0]}", use_logo=False),
                    self._build_rent_row("2 предприятия", f"×{mult[1]}", use_logo=False, is_bold=True),
                    ft.Divider(height=20, thickness=2, color="black"),
                    self._build_rent_row("Стоимость покупки", data["price"], is_small=True),
                    self._build_rent_row("Залоговая стоимость", data["mortgage"], is_small=True),
                    self._build_card_buttons(index, purchase_mode, cell_name, data["price"]),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, tight=True
            )
            self.card_layer.content = ft.Container(
                content=ft.Container(width=300, padding=10, bgcolor="white",
                    border_radius=10, border=ft.Border.all(2, "black"),
                    content=card_content),
                alignment=ft.Alignment.CENTER, expand=True,
            )
            self.card_layer.visible = True
            self.update()
            return

        # ========== УЛИЦЫ ==========
        group_color = CELL_COLORS.get(index, "#00000000")
        rent_data = get_card_info(cell_name)
        if rent_data is None:
            return
        rent = rent_data["rent"]
        text_color = "#000000"
        card_content = ft.Column(
            [
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text("ПРАВО СОБСТВЕННОСТИ", size=10, weight="bold", color=text_color),
                            ft.Text(
                                rent_data["название"],
                                size=18,
                                weight="bold",
                                color=text_color,
                                text_align=ft.TextAlign.CENTER
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                    ),
                    bgcolor=group_color,
                    padding=ft.Padding.all(10),
                    width=280,
                    border=ft.Border.all(2, "black"),
                ),
                ft.Container(height=10),
                self._build_rent_row("Плата за просто улицу", rent[0], is_bold=True),
                ft.Divider(height=10, thickness=1, color="#EEEEEE"),
                self._build_rent_row("С 1 уровнем развития", rent[1]),
                self._build_rent_row("С 2 уровнями развития", rent[2]),
                self._build_rent_row("С 3 уровнями развития", rent[3]),
                self._build_rent_row("С 4 уровнями развития", rent[4]),
                ft.Container(height=5),
                self._build_rent_row("УРОВЕНЬ 5 ", rent[5], is_bold=True),
                ft.Divider(height=20, thickness=2, color="black"),
                self._build_rent_row("Стоимость покупки", rent_data["цена"], is_small=True),
                self._build_rent_row("Залоговая стоимость", int(int(rent_data["цена"]) * 0.5), is_small=True),
                self._build_rent_row("Стоимость уровня", rent_data["star"], is_small=True),
                self._build_card_buttons(index, purchase_mode, cell_name, rent_data["цена"]),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=0, tight=True
        )
        self.card_layer.content = ft.Container(
            content=ft.Container(width=300, padding=10, bgcolor="white",
                border_radius=10, border=ft.Border.all(2, "black"),
                content=card_content),
            alignment=ft.Alignment.CENTER, expand=True,
        )
        self.card_layer.visible = True
        self.update()


    def close_card(self, e=None):
        self.card_layer.visible = False
        self.card_layer.content = None
        # После закрытия карточки показываем кнопку завершения хода, если игра уже началась
        self.update()

    def update_ownership(self, owners: dict, money_dict: dict = None, levels: dict = None, dict_pawn: dict = None, balance: dict = None, player_color: dict = None):
        if player_color is not None:
            self.set_player_colors(player_color)
        if dict_pawn is not None:
            self.pawned_cells = {int(k) for k, v in dict_pawn.items() if v}
        if levels is not None:
            merged = dict(getattr(self, "property_levels", {}))
            for k, v in levels.items():
                merged[int(k)] = int(v)
            self.update_levels(merged)
        # 1. Конвертируем ключи клеток в int
        self.property_owners = {}
        for k, v in owners.items():
            try:
                if v not in getattr(self, "_left_players", set()):
                    if v not in self._left_players:
                        self.property_owners[int(k)] = v
            except (ValueError, TypeError):
                pass


        # 2. Обновляем деньги (ТЕПЕРЬ ЭТО DICT)
        if money_dict is not None:
            for name, money in money_dict.items():
                self.player_balances[name] = money

            self.config.money = money_dict
            self.update_balance_display()
        if balance is not None:
            for name, b in balance.items():
                self.player_balance[name] = b

        # 3. Обновляем визуал владения
        self.apply_ownership_visuals()
        self.update_pawn_visuals()

        # 4. Обновляем UI
        self.update()

    async def check_and_offer_purchase(self, username: str, cell_index: int):
        if cell_index not in CELL_DATA:
            return
        cell_name = CELL_DATA[cell_index]

        if cell_name == "Эко-сбор":
            if username == self.config.username:
                self._last_payment = {"action": "remove_token", "username": username, "payments": 200, "amount": 200}
                websocket.send_action("remove_token", username = username, payments = 200)
                self.end_turn_button.visible = True
            await self.remove_money(username, 200, cell_name)
            return

        if cell_name == "Налог на выбросы CO2":
            if username == self.config.username:
                self._last_payment = {"action": "remove_token", "username": username, "payments": 100, "amount": 100}
                websocket.send_action("remove_token", username = username, payments = 100)
                self.end_turn_button.visible = True
            await self.remove_money(username, 100, cell_name)
            return
        

        # === ЭКО-КВЕСТ ===
        if cell_name == "Эко-квест":
            if username == self.config.username:
                websocket.send_action("eco_quest_trigger", username=username)
                self.end_turn_button.visible = False
                self.update()
            return

        is_buyable = (cell_name in STREETS_DATA or
                      cell_name in TRANSPORT_DATA or
                      cell_name in UTILITY_DATA)

        if not is_buyable:
            if username == self.config.username:
                self.end_turn_button.visible = True
                self.update()
            return

        owner = self.property_owners.get(cell_index)

        # ЧУЖАЯ СОБСТВЕННОСТЬ — ПЛАТИМ РЕНТУ
        if owner is not None and owner != username:
            if cell_index in self.pawned_cells:
                asyncio.create_task(self.show_pawned_message(cell_name))
                if username == self.config.username:
                    self.end_turn_button.visible = True
                    self.update()
                return
            rent = self._calculate_rent(cell_index, owner)
            if rent > 0 and username == self.config.username:
                # Отправляем на сервер — сервер спишет и пришлёт rent_paid всем
                self._last_payment = {"action": "pay_rent", "username": username, "owner": owner,
                                      "cell_index": cell_index, "amount": rent}
                websocket.send_action('pay_rent',
                    username=username,
                    owner=owner,
                    cell_index=cell_index,
                    amount=rent)
            # Кнопку НЕ показываем — она появится после анимации в обработчике rent_paid
            return

        # СВОЯ СОБСТВЕННОСТЬ
        if owner == username:
            if username == self.config.username:
                self.end_turn_button.visible = True
                self.update()
            return
        print("сейчас будет улица")
        # СВОБОДНАЯ КЛЕТКА
        if owner is None:
            print("свободная")
            if username != self.config.username:
                return
            self.end_turn_button.visible = False
            self.update()
            self.show_cell_info(cell_index, purchase_mode=True)

    def _calculate_rent(self, cell_index: int, owner: str) -> int:
        """Рассчитывает ренту для клетки"""
        cell_name = CELL_DATA.get(cell_index)
        if not cell_name:
            return 0

        # ===== УЛИЦЫ =====
        if cell_name in STREETS_DATA:
            data = STREETS_DATA[cell_name]
            if cell_index in self.pawned_cells:
                return 0
            # Пока без домов — базовая рента (уровень 0)
            # TODO: добавить учёт уровней развития
            level = self.property_levels.get(cell_index, 0)

            # Проверяем монополию (все улицы группы у одного владельца)
            has_monopoly = self._check_monopoly(cell_index, owner)

            rent = data["rent"][level]

            # Если монополия и нет домов — рента удваивается
            if has_monopoly and level == 0:
                rent *= 2

            return rent

        # ===== ТРАНСПОРТ =====
        if cell_name in TRANSPORT_DATA:
            # Считаем сколько транспортных компаний у владельца
            transport_count = 0
            for t_idx in TRANSPORT_INDICES:
                if self.property_owners.get(t_idx) == owner:
                    transport_count += 1

            data = TRANSPORT_DATA[cell_name]
            if transport_count > 0:
                return data["rent"][transport_count - 1]
            return 0

        # ===== КОММУНАЛКА =====
        if cell_name in UTILITY_DATA:
            # Считаем сколько предприятий у владельца
            utility_count = 0
            for u_idx in UTILITY_INDICES:
                if self.property_owners.get(u_idx) == owner:
                    utility_count += 1

            data = UTILITY_DATA[cell_name]
            # Множитель зависит от количества предприятий
            multiplier = data["multiplier"][utility_count - 1] if utility_count > 0 else 0

            # Рента = последний бросок кубиков * множитель
            # Берём последний бросок из dice_display
            try:
                dice_row = self.dice_display.content.controls
                d1 = int(dice_row[0].content.value)
                d2 = int(dice_row[1].content.value)
                dice_sum = d1 + d2
            except (ValueError, AttributeError):
                dice_sum = 7  # fallback

            return dice_sum * multiplier

        return 0

    def _check_monopoly(self, cell_index: int, owner: str) -> bool:
        """Проверяет, владеет ли owner всеми улицами той же цветной группы"""
        cell_color = CELL_COLORS.get(cell_index)
        if not cell_color:
            return False

        # Находим все клетки с таким же цветом
        group_indices = [idx for idx, color in CELL_COLORS.items() if color == cell_color]

        # Проверяем что все принадлежат owner
        for idx in group_indices:
            if self.property_owners.get(idx) != owner:
                return False
        return True


    async def start_auction(self, cell_index: int):
        websocket.send_action('start_auction', username=self.config.username, cell_index=cell_index)
        self.card_layer.visible = False
        self.card_layer.content = None
        self.pending_purchase_cell = None
        self.update()


    async def show_auction_dialog(
        self,
        cell_index: int,
        cell_name: str,
        start_price: int,
        current_bid: int,
        current_leader,
        initiator: str,
        bid_history: list = None,
        time_left: int = 5,
        is_initiator: bool = False,
    ):
        # Если окно уже открыто — просто обновляем данные, не пересоздаём
        if self._auction_overlay:
            self._auction_queue.append(dict(
                cell_index=cell_index, cell_name=cell_name, start_price=start_price,
                current_bid=current_bid, current_leader=current_leader, initiator=initiator,
                bid_history=bid_history or [], time_left=time_left, is_initiator=is_initiator,
            ))
            return

        # Запоминаем кто запустил аукцион и ПОЛНОСТЬЮ прячем кнопки хода
        self._auction_initiator = initiator
        self.end_turn_button.visible = False
        self.roll_button.visible = False

        self._auction_state = {
            "cell_index": cell_index,
            "cell_name": cell_name,
            "start_price": start_price,
            "current_bid": current_bid,
            "current_leader": current_leader,
            "initiator": initiator,
        }
        self._auction_time_left = time_left

        property_card = self._build_auction_property_card(
            cell_index=cell_index,
            cell_name=cell_name,
            current_bid=current_bid,
            current_leader=current_leader,
        )

        self._auction_bid_text = ft.Text(
            str(current_bid),
            size=15,
            weight=ft.FontWeight.BOLD,
            color="#234746",
        )

        self._auction_leader_text = ft.Text(
            current_leader if current_leader else "—",
            size=15,
            weight=ft.FontWeight.BOLD,
            color="#234746",
        )

        self._auction_timer_text = ft.Text(
            f"{time_left} сек" if current_leader else "Ждём ставку",
            size=15,
            weight=ft.FontWeight.BOLD,
            color="#D32F2F" if current_leader else "#666666",
        )

        self._auction_balance_text = ft.Text(
            str(self.player_balance.get(self.config.username, 0)),
            size=15, weight=ft.FontWeight.BOLD, color="#1B5E20",
        )
        right_panel = ft.Container(
            width=360,
            bgcolor="white",
            border_radius=40,
            border=ft.Border.all(3, "black"),
            padding=20,
            content=ft.Column(
                [
                    ft.Text(
                        "ИНФОРМАЦИЯ\nО АУКЦИОНЕ",
                        size=20,
                        weight=ft.FontWeight.BOLD,
                        color="#111111",
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Container(height=10),
                    ft.Divider(color="#222222", thickness=1.5),
                    ft.Container(height=20),
                    ft.Row(
                        [
                            ft.Text("Текущая ставка:", size=15, color="#234746", weight=ft.FontWeight.W_600),
                            ft.Row(
                                [self._auction_bid_text, ft.Image(src=ECO_COIN_LOGO, width=16, height=16)],
                                spacing=4, tight=True,
                            )
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [ft.Text("Лидер:", size=15, color="#234746", weight=ft.FontWeight.W_600),
                         self._auction_leader_text],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Row(
                        [ft.Text("Таймер:", size=15, color="#234746", weight=ft.FontWeight.W_600),
                         self._auction_timer_text],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                 ft.Row(
                     [ft.Text("Твой баланс:", size=15, color="#234746", weight=ft.FontWeight.W_600),
                      self._auction_balance_text],
                     alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                 ),
                ],
                spacing=12,
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        auction_card = ft.Container(
            width=720,
            bgcolor="transparent",
            content=ft.Row(
                [property_card, ft.Container(width=40), right_panel],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
        )

        self._auction_overlay = ft.Container(
            content=auction_card,
            expand=True,
            bgcolor="#88000000",
            alignment=ft.Alignment.CENTER,
        )

        main_stack = self.controls[0]
        main_stack.controls.append(self._auction_overlay)

        self.update()
        if self.page:
            self.page.update()

        if current_leader or (initiator and initiator not in self.config.usernames):
            self._reset_auction_timer(
                is_initiator=(self.config.username == initiator
                              or initiator not in self.config.usernames)
            )


    def _build_simple_auction_card(self, cell_index, cell_name, start_price, group_color):
        """Простая карточка — как при покупке"""
        text_color = "#000" if group_color == "#FFF004" else "white"
        return ft.Container(
            width=450, bgcolor="white", border_radius=8, border=ft.Border.all(2, "black"),
            content=ft.Column([
                ft.Container(content=ft.Text(cell_name.upper(), size=12, weight="bold", color=text_color, text_align=ft.TextAlign.CENTER), bgcolor=group_color, padding=6, border_radius=ft.border_radius.only(top_left=6, top_right=6)),
                ft.Container(padding=8, content=ft.Column([
                    self._build_rent_row("Цена", start_price, is_small=True),
                    self._build_rent_row("Залог", start_price//2, is_small=True),
                ], spacing=2)),
            ], spacing=0),
        )
    
    def _build_auction_property_card(self, cell_index, cell_name, start_price, group_color):
        """Карточка как при покупке — компактная"""
        text_color = "#000000" if group_color == "#FFF004" else "white"
        
        # Базовая информация
        info_rows = [
            self._build_rent_row("Стартовая цена", start_price, is_small=True),
            self._build_rent_row("Залог", start_price // 2, is_small=True),
        ]
        
        # Рента (если улица)
        if cell_name in STREETS_DATA:
            rent = STREETS_DATA[cell_name]["rent"][0]
            info_rows.append(self._build_rent_row("Базовая рента", rent, is_small=True))
        elif cell_name in TRANSPORT_DATA:
            info_rows.append(self._build_rent_row("Рента (1 компания)", TRANSPORT_DATA[cell_name]["rent"][0], is_small=True))
        elif cell_name in UTILITY_DATA:
            info_rows.append(self._build_rent_row("Множитель", f"×{UTILITY_DATA[cell_name]['multiplier'][0]}", is_small=True, use_logo=False))
        
        return ft.Container(
            width=520,
            bgcolor="white",
            border_radius=10,
            border=ft.Border.all(2, "black"),
            content=ft.Column(
                spacing=0,
                controls=[
                    ft.Container(
                        content=ft.Text(cell_name.upper(), size=13, weight=ft.FontWeight.BOLD, color=text_color, text_align=ft.TextAlign.CENTER),
                        bgcolor=group_color,
                        padding=8,
                        border_radius=ft.border_radius.only(top_left=8, top_right=8),
                    ),
                    ft.Container(
                        padding=10,
                        content=ft.Column(spacing=2, controls=info_rows),
                    ),
                ],
            ),
        )
    
    
    def on_auction_update(self, current_bid: int, current_leader: str, bid_history: list = None, time_left: int = 5):
        self.update_auction_ui(current_bid, current_leader, time_left)

        if current_leader:
            initiator = self._auction_state.get("initiator")
            self._reset_auction_timer(
                is_initiator=(self.config.username == initiator
                              or initiator not in self.config.usernames)
            )
    
    
    async def on_auction_won(self, winner: str, final_bid: int, cell_index: int, my_username: str, initiator: str = None):
        auction_initiator = self._auction_initiator
        payment_mode_was_active = getattr(self, "_payment_mode", False)

        # Всегда закрываем сам аукцион.
        self.close_auction()

        if payment_mode_was_active:
            # Это именно завершение ранее созданного долга аукциона.
            # Не показываем ещё один полноэкранный результат поверх
            # карточки «Не хватает монет» и не оставляем sell/pawn mode.
            self.exit_payment_mode(enable_end_turn=False)

            # Ход принадлежит инициатору аукциона.
            # Поэтому кнопку завершения хода получает только инициатор.
            if my_username in (auction_initiator, initiator):
                self._set_end_turn_enabled(True)
            else:
                self.end_turn_button.visible = False
                self.end_turn_button.disabled = True
                self.end_turn_button.update()
            self.update()
            if self.page:
                self.page.update()
            return

        # Обычное завершение аукциона — оставляем прежний экран результата.
        if getattr(self, "_sell_mode", False):
            self.exit_sell_mode()
        if getattr(self, "_pawn_mode", False):
            self.exit_pawn_mode()

        winner_color = self.player_border_color.get(winner, "#234746")

        result_card = ft.Container(
            width=400,
            bgcolor="white",
            border_radius=16,
            border=ft.Border.all(3, winner_color),
            padding=ft.Padding.all(30),
            shadow=ft.BoxShadow(blur_radius=20, color="#44000000"),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=12,
                controls=[
                    ft.Text("АУКЦИОН ЗАВЕРШЁН", size=14, color="#999999", weight=ft.FontWeight.BOLD),
                    ft.Text("🏆 Победитель", size=16, color="#234746"),
                    ft.Text(winner, size=28, weight=ft.FontWeight.BOLD, color=winner_color),
                    ft.Row(
                        [ft.Image(src=r"..\assets\экокоин.png", width=28, height=28),
                         ft.Text(str(final_bid), size=28, weight=ft.FontWeight.BOLD, color="#234746")],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=8,
                    ),
                ],
            ),
        )

        result_overlay = ft.Container(
            content=result_card,
            expand=True,
            bgcolor="#AA000000",
            alignment=ft.Alignment.CENTER,
        )

        main_stack = self.controls[0]
        main_stack.controls.append(result_overlay)
        self.update()
        if self.page:
            self.page.update()

        await asyncio.sleep(3)

        if result_overlay in main_stack.controls:
            main_stack.controls.remove(result_overlay)

        # ПОКАЗЫВАЕМ КНОПКУ ТОЛЬКО ТОМУ, КТО ЗАПУСКАЛ АУКЦИОН
        if my_username in (auction_initiator, initiator):
            self.end_turn_button.visible = True

        self._auction_initiator = None
        self.update()
        if self.page:
            self.page.update()
    
    
    def close_auction(self):
        if self._auction_queue:
            nxt = self._auction_queue.pop(0)
            asyncio.create_task(self.show_auction_dialog(**nxt))
        if self._auction_timer_task:
            self._auction_timer_task.cancel()
            self._auction_timer_task = None

        if self._auction_overlay:
            main_stack = self.controls[0]
            if self._auction_overlay in main_stack.controls:
                main_stack.controls.remove(self._auction_overlay)
            self._auction_overlay = None

        self._auction_state = {}
        self._auction_history = []
        self._auction_timer_text = None
        self._auction_timer_bar = None
        self._auction_history_column = None
        self._auction_bid_text = None
        self._auction_leader_text = None
        self._auction_left_btn = None
        self._auction_right_btn = None
        self._auction_left_btn_text = None
        self._auction_right_btn_text = None
        self._auction_initiator = None

        self.update()
        if self.page:
            self.page.update()
    
    
    async def _send_auction_end(self):
        """Инициатор завершает аукцион."""
        websocket.send_action("auction_end", username=self.config.username)
    
    
    # ── Обновляем _build_card_buttons ─────────────────────────────────────
    
    def _build_card_buttons(self, cell_index: int, purchase_mode: bool, cell_name: str, price: int = None):
        if purchase_mode:
            my_balance = self.player_balance.get(self.config.username, 0)
            can_afford = my_balance >= price
            
            buy_button = ft.Button(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.SHOPPING_CART,
                            color="white" if can_afford else "#BDBDBD",
                            size=18,
                        ),
                        ft.Text(
                            "Купить",
                            size=14,
                            weight=ft.FontWeight.BOLD,
                            color="white" if can_afford else "#BDBDBD",
                        ),
                    ],
                    tight=True,
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                disabled=not can_afford,
                on_click=lambda e: asyncio.create_task(self.buy_property(cell_index, price)),
                style=ft.ButtonStyle(
                    bgcolor={ 
                        "": "#2E7D32" if can_afford else "#9E9E9E",
                        ft.ControlState.DISABLED: "#9E9E9E",
                        ft.ControlState.HOVERED: "#1B5E20" if can_afford else "#9E9E9E",
                    },
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                ),
            )
    
            auction_button = ft.Button(
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.GAVEL, color="white", size=18),
                        ft.Text("Аукцион", size=14, weight=ft.FontWeight.BOLD, color="white"),
                    ],
                    tight=True,
                    spacing=8,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                on_click=lambda e: asyncio.create_task(
                    self._initiate_auction(cell_index, cell_name, price)
                ),
                style=ft.ButtonStyle(
                    bgcolor={"": "#FF8C00", ft.ControlState.HOVERED: "#E65100"},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=16, vertical=10),
                ),
            )
    
            # Подсказка если нет денег
            hint = ft.Text(
                f"Не хватает {price - my_balance} М" if not can_afford else "",
                size=11,
                color="#CC0000",
                text_align=ft.TextAlign.CENTER,
            )
    
            return ft.Column(
                [
                    ft.Row(
                        [buy_button, auction_button],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=16,
                    ),
                    hint,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=4,
                tight=True,
            )
        else:
            return ft.Container(
                content=ft.Button(
                    content=ft.Text("ЗАКРЫТЬ", size=14, weight=ft.FontWeight.BOLD, color="white"),
                    on_click=self.close_card,
                    style=ft.ButtonStyle(
                        bgcolor={"": "#234746"},
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.symmetric(horizontal=30, vertical=10),
                    ),
                ),
                alignment=ft.Alignment.CENTER,
            )
    
    
    async def _initiate_auction(self, cell_index: int, cell_name: str, price: int):
        """Отправляет на сервер запрос на начало аукциона с РАСЧИТАННОЙ ценой"""
        self.card_layer.visible = False
        self.card_layer.content = None
        self.update()
    
        # 🔥 КЛИЕНТ считает стартовую ставку (10% от цены, минимум 10)
        start_price = 0
        
        websocket.send_action(
            "start_auction",
            username=self.config.username,
            cell_index=cell_index,
            cell_name=cell_name,  # Для отображения/логов
            start_price=start_price,  # 🔥 Передаём рассчитанную цену
        )

    def _full_monopoly_colors(self, username):
        colors = set()
        for idx, owner in self.property_owners.items():
            if owner == username and idx in CELL_COLORS:
                colors.add(CELL_COLORS[idx])
        full = []
        for color in colors:
            idxs = [i for i, c in CELL_COLORS.items() if c == color]
            if idxs and all(self.property_owners.get(i) == username for i in idxs):
                full.append(color)
        return full

    def _set_end_turn_enabled(self, enabled: bool):
        btn = self.end_turn_button.content
        btn.disabled = not enabled
        btn.style = ft.ButtonStyle(
            bgcolor={"": "#234746" if enabled else "#9E9E9E",
                     ft.ControlState.HOVERED: "#1b3837" if enabled else "#9E9E9E",
                     ft.ControlState.DISABLED: "#9E9E9E"},
            shape=ft.RoundedRectangleBorder(radius=8),
            padding=ft.Padding.symmetric(horizontal=15, vertical=10),
        )
        self.end_turn_button.update()

    def update(self):
        super().update()
        me = self.config.username

        # Режим погашения долга по аукциону имеет приоритет над обычными
        # режимами. Игрок может только продать уровень или заложить имущество.
        if getattr(self, "_payment_mode", False):
            self.roll_button.visible = False
            self.end_turn_button.visible = True
            self._set_end_turn_enabled(False)
            self.upgrade_wrap.visible = False
            self.pawn_wrap.visible = True
            self.sell_wrap.visible = True
            self.pawn_wrap.update()
            self.sell_wrap.update()
            self.upgrade_wrap.update()
            return

        want_up = (
            self.end_turn_button.visible
            and not self.is_rolling_phase
            and len(self._full_monopoly_colors(me)) > 0
        )
        if hasattr(self, "upgrade_wrap") and self.upgrade_wrap.visible != want_up:
            self.upgrade_wrap.visible = want_up
            self.upgrade_wrap.update()
        pending = getattr(self, "_pending_payment", None) is not None
        want_pawn = (
            (self.end_turn_button.visible
             and not self.is_rolling_phase
             and self._owns_any_street(me))
            or pending
        )
        if hasattr(self, "pawn_wrap") and self.pawn_wrap.visible != want_pawn:
            self.pawn_wrap.visible = want_pawn
            self.pawn_wrap.update()
        want_sell = want_up or pending
        if hasattr(self, "sell_wrap") and self.sell_wrap.visible != want_sell:
            self.sell_wrap.visible = want_sell
            self.sell_wrap.update()

    def upgrade_action(self, e):
        if self._upgrade_mode:
            self.exit_upgrade_mode()
            return
        if self._pawn_mode:
            self.exit_pawn_mode()
        if self._sell_mode:
            self.exit_sell_mode()
        self._upgrade_mode = True
        self._upgrade_pending = False
        self._set_end_turn_enabled(False)
        me = self.config.username
        full = self._full_monopoly_colors(me)
        my_balance = self.player_balances.get(me, 0)
        self._upgrade_cells = []
        for idx, owner in self.property_owners.items():
            if owner != me or CELL_COLORS.get(idx) not in full:
                continue
            group_idxs = [i for i, c in CELL_COLORS.items() if c == CELL_COLORS[idx]]
            min_lvl = min(self.property_levels.get(i, 0) for i in group_idxs)
            lvl = self.property_levels.get(idx, 0)
            star = STREETS_DATA.get(CELL_DATA.get(idx), {}).get("star", 0)
            if lvl == min_lvl and lvl < 5 and my_balance >= star:
                cell = self.cells_objects.get(idx)
                if cell:
                    cell.border = ft.Border.all(3, "#2E7D32")
                    cell.update()
                    self._upgrade_cells.append(idx)
        self.update()

    def exit_upgrade_mode(self):
        for idx in self._upgrade_cells:
            cell = self.cells_objects.get(idx)
            if cell:
                cell.border = None
                cell.update()
        self._upgrade_cells = []
        self._upgrade_mode = False
        self._upgrade_pending = False
        self._set_end_turn_enabled(True)
        self.update()

    def try_upgrade_cell(self, index):
        if self._upgrade_pending:
            return
        if index not in self._upgrade_cells:
            return
        self._upgrade_pending = True
        cell_name = CELL_DATA.get(index)
        star = STREETS_DATA.get(cell_name, {}).get("star", 0)
        websocket.send_action("upgrade_level", username=self.config.username, cell_index=index, level=star)
        asyncio.create_task(self._upgrade_timeout())

    async def _upgrade_timeout(self):
        await asyncio.sleep(3)
        if self._upgrade_pending:
            self._upgrade_pending = False
            self.update()

    def on_upgrade_result(self, data: dict):
        """ВЫЗЫВАЙ ИЗ ОБРАБОТЧИКА: utils.game.on_upgrade_result(data)"""
        self._upgrade_pending = False
        levels = data.get("levels")
        if levels is not None:
            merged = dict(self.property_levels)
            for k, v in levels.items():
                merged[int(k)] = int(v)
            self.update_levels(merged)
        self._sync_money(data)
        was_ok = data.get("ok", False)
        self.exit_upgrade_mode()
        if was_ok and data.get("username") == self.config.username and self._can_upgrade_any():
            self.upgrade_action(None)
        self.update()

    def _can_upgrade_any(self):
        me = self.config.username
        my_balance = self.player_balances.get(me, 0)
        for color in self._full_monopoly_colors(me):
            idxs = [i for i, c in CELL_COLORS.items() if c == color]
            min_lvl = min(self.property_levels.get(i, 0) for i in idxs)
            for idx in idxs:
                lvl = self.property_levels.get(idx, 0)
                if lvl != min_lvl or lvl >= 5:
                    continue
                star = STREETS_DATA.get(CELL_DATA.get(idx), {}).get("star", 0)
                if my_balance >= star:
                    return True
        return False

    def update_levels(self, levels: dict):
        self.property_levels = {int(k): int(v) for k, v in levels.items()}
        if not hasattr(self, '_level_blocks'):
            self._level_blocks = []
        for b in self._level_blocks:
            if b in self.grid_overlay.content.controls:
                self.grid_overlay.content.controls.remove(b)
        self._level_blocks.clear()
        board_size = self.height_ - 20
        corner_coef = 1.6
        std_w = board_size / (9 + 2 * corner_coef)
        corner_w = std_w * corner_coef
        strip_thick = 14
        strip_margin = 4
        size = 12
        gap = 2
        for idx, level in self.property_levels.items():
            if level <= 0:
                continue
            level = min(level, 5)
            total = level * size + (level - 1) * gap
            if 0 < idx < 10:
                strip_len = std_w - 2 * strip_margin
                cell_right_edge = corner_w + (idx - 1) * std_w
                sx = board_size - cell_right_edge - std_w + strip_margin
                sy = board_size - corner_w + 2
                horizontal = True
            elif 10 < idx < 20:
                strip_len = std_w - 2 * strip_margin
                sx = corner_w - size - 2
                sy = board_size - (corner_w + (idx - 11) * std_w) - std_w + strip_margin
                horizontal = False
            elif 20 < idx < 30:
                strip_len = std_w - 2 * strip_margin
                sx = corner_w + (idx - 21) * std_w + strip_margin
                sy = corner_w - size - 2
                horizontal = True
            elif 30 < idx < 40:
                strip_len = std_w - 2 * strip_margin
                sx = board_size - corner_w + 2
                sy = corner_w + (idx - 31) * std_w + strip_margin
                horizontal = False
            else:
                continue
            start = (strip_len - total) / 2
            for i in range(level):
                off = start + i * (size + gap)
                if horizontal:
                    lx, ly = sx + off, sy
                else:
                    lx, ly = sx, sy + off
                leaf = ft.Container(
                    content=ft.Icon(ft.Icons.ECO, color="#2E7D32", size=10),
                    width=size, height=size, bgcolor="white",
                    shape=ft.BoxShape.CIRCLE, border=ft.Border.all(1.5, "#2E7D32"),
                    alignment=ft.Alignment.CENTER,
                    left=lx, top=ly,
                )
                self._level_blocks.append(leaf)
                self.grid_overlay.content.controls.append(leaf)
        self.grid_overlay.update()

    def sell_action(self, e):
        if getattr(self, "_payment_mode", False):
            self._payment_selection = "sell"
            self._sell_mode = True
            self._pawn_mode = False
            self._pawn_cells = []
            self._redeem_cells = []
            self._highlight_payment_sell_cells()
            self.update()
            return
        if self._sell_mode:
            self.exit_sell_mode()
            return
        if self._upgrade_mode:
            self.exit_upgrade_mode()
        self._sell_mode = True
        self._sell_pending = False
        self._set_end_turn_enabled(False)
        me = self.config.username
        full = self._full_monopoly_colors(me)
        self._sell_cells = []
        for idx, owner in self.property_owners.items():
            if owner != me or CELL_COLORS.get(idx) not in full:
                continue
            group_idxs = [i for i, c in CELL_COLORS.items() if c == CELL_COLORS[idx]]
            max_lvl = max(self.property_levels.get(i, 0) for i in group_idxs)
            lvl = self.property_levels.get(idx, 0)
            if lvl == max_lvl and lvl > 0:
                cell = self.cells_objects.get(idx)
                if cell:
                    cell.border = ft.Border.all(3, "#E65100")
                    cell.update()
                    self._sell_cells.append(idx)
        self.update()

    def exit_sell_mode(self):
        for idx in self._sell_cells:
            cell = self.cells_objects.get(idx)
            if cell:
                cell.border = None
                cell.update()
        self._sell_cells = []
        self._sell_mode = False
        self._sell_pending = False
        self._set_end_turn_enabled(True)
        self.update()

    def try_sell_cell(self, index):
        if self._sell_pending:
            return
        if index not in self._sell_cells:
            return
        self._sell_pending = True
        cell_name = CELL_DATA.get(index)
        star = STREETS_DATA.get(cell_name, {}).get("star", 0)
        websocket.send_action("sell_level", username=self.config.username, cell_index=index, level=star)
        asyncio.create_task(self._sell_timeout())

    async def _sell_timeout(self):
        await asyncio.sleep(3)
        if self._sell_pending:
            self._sell_pending = False
            self.update()

    def on_sell_result(self, data: dict):
        """Обрабатывает продажу уровня. В режиме погашения долга
        не возвращаем обычный режим продажи и не включаем кнопку хода.
        """
        self._sell_pending = False
        self._apply_money(data)
        levels = data.get("levels")
        if levels is not None:
            merged = dict(self.property_levels)
            for k, v in levels.items():
                merged[int(k)] = int(v)
            self.update_levels(merged)

        if getattr(self, "_payment_mode", False):
            # После одной продажи остаёмся в режиме погашения,
            # но сами режимы выбора клетки выключаем.
            self._sell_mode = False
            self._pawn_mode = False
            self._clear_payment_highlights()
            self._set_end_turn_enabled(False)
            self.pawn_wrap.visible = True
            self.sell_wrap.visible = True
            self._payment_selection = None
        else:
            was_ok = data.get("ok", False)
            self.exit_sell_mode()
            if was_ok and data.get("username") == self.config.username and self._can_sell_any():
                self.sell_action(None)

        self._try_repay()
        self.update()

    def _can_sell_any(self):
        me = self.config.username
        for color in self._full_monopoly_colors(me):
            idxs = [i for i, c in CELL_COLORS.items() if c == color]
            max_lvl = max(self.property_levels.get(i, 0) for i in idxs)
            if max_lvl > 0:
                return True
        return False

    def _owns_any_street(self, username):
        return any(
            owner == username and (CELL_DATA.get(idx) in STREETS_DATA
                                   or CELL_DATA.get(idx) in TRANSPORT_DATA
                                   or CELL_DATA.get(idx) in UTILITY_DATA)
            for idx, owner in self.property_owners.items()
        )

    def exit_payment_mode(self, enable_end_turn: bool = False):
        """Полностью завершает режим погашения долга.

        В отличие от exit_pawn_mode()/exit_sell_mode() не включает
        кнопку завершения хода автоматически. Это важно для выхода
        из payment mode после auction_won.
        """
        self._clear_payment_highlights()
        self._payment_mode = False
        self._payment_amount = 0
        self._payment_selection = None
        self._pending_payment = None
        self._pawn_mode = False
        self._sell_mode = False
        self._pawn_pending = False
        self._sell_pending = False
        self.roll_button.visible = False
        self.upgrade_wrap.visible = False
        self.pawn_wrap.visible = False
        self.sell_wrap.visible = False
        self._set_end_turn_enabled(enable_end_turn)
        self.update()

    def _clear_payment_highlights(self):
        for idx in list(self._sell_cells) + list(self._pawn_cells) + list(getattr(self, "_redeem_cells", [])):
            cell = self.cells_objects.get(idx)
            if cell:
                cell.border = None
                cell.update()
        self._sell_cells = []
        self._pawn_cells = []
        self._redeem_cells = []

    def _highlight_payment_pawn_cells(self):
        self._clear_payment_highlights()
        me = self.config.username
        for idx, owner in self.property_owners.items():
            if owner != me or idx in self.pawned_cells:
                continue
            cell = self.cells_objects.get(idx)
            if not cell:
                continue
            name = CELL_DATA.get(idx)
            if name in STREETS_DATA and self.property_levels.get(idx, 0) != 0:
                continue
            if name in STREETS_DATA or name in TRANSPORT_DATA or name in UTILITY_DATA:
                cell.border = ft.Border.all(3, "#E65100")
                cell.update()
                self._pawn_cells.append(idx)

    def _highlight_payment_sell_cells(self):
        self._clear_payment_highlights()
        me = self.config.username
        full = self._full_monopoly_colors(me)
        for idx, owner in self.property_owners.items():
            if owner != me or CELL_COLORS.get(idx) not in full:
                continue
            group_idxs = [i for i, c in CELL_COLORS.items() if c == CELL_COLORS[idx]]
            max_lvl = max(self.property_levels.get(i, 0) for i in group_idxs)
            lvl = self.property_levels.get(idx, 0)
            if lvl == max_lvl and lvl > 0:
                cell = self.cells_objects.get(idx)
                if cell:
                    cell.border = ft.Border.all(3, "#E65100")
                    cell.update()
                    self._sell_cells.append(idx)

    def pawn_action(self, e):
        if getattr(self, "_payment_mode", False):
            self._payment_selection = "pawn"
            self._pawn_mode = True
            self._sell_mode = False
            self._sell_cells = []
            self._highlight_payment_pawn_cells()
            self.update()
            return
        if self._pawn_mode:
            self.exit_pawn_mode()
            return
        if getattr(self, "_upgrade_mode", False):
            self.exit_upgrade_mode()
        if getattr(self, "_sell_mode", False):
            self.exit_sell_mode()
        self._pawn_mode = True
        self._set_end_turn_enabled(False)
        self._highlight_pawn_cells()
        self.update()

    def _highlight_pawn_cells(self):
        self._pawn_pending = False
        me = self.config.username
        my_balance = self.player_balances.get(me, 0)
        for idx in list(self._pawn_cells) + list(getattr(self, "_redeem_cells", [])):
            cell = self.cells_objects.get(idx)
            if cell:
                cell.border = None
                cell.update()
        self._pawn_cells = []
        self._redeem_cells = []
        for idx, owner in self.property_owners.items():
            if owner != me:
                continue
            cell = self.cells_objects.get(idx)
            if not cell:
                continue
            name = CELL_DATA.get(idx)
            if idx in self.pawned_cells:
                if my_balance >= self._cell_price(idx) // 2:
                    cell.border = ft.Border.all(3, "#2E7D32")
                    cell.update()
                    self._redeem_cells.append(idx)
                continue
            if name in STREETS_DATA:
                if self.property_levels.get(idx, 0) != 0:
                    continue
                cell.border = ft.Border.all(3, "#E65100")
                cell.update()
                self._pawn_cells.append(idx)
            elif name in TRANSPORT_DATA or name in UTILITY_DATA:
                cell.border = ft.Border.all(3, "#E65100")
                cell.update()
                self._pawn_cells.append(idx)

    def exit_pawn_mode(self):
        for idx in list(self._pawn_cells) + list(getattr(self, "_redeem_cells", [])):
            cell = self.cells_objects.get(idx)
            if cell:
                cell.border = None
                cell.update()
        self._pawn_cells = []
        self._redeem_cells = []
        self._pawn_mode = False
        self._pawn_pending = False
        self._set_end_turn_enabled(True)
        self.update()

    def try_pawn_cell(self, index):
        if self._pawn_pending:
            return
        if index in self._pawn_cells:
            self._pawn_pending = True
            websocket.send_action("pawn", username=self.config.username,
                                  cell_index=index, value=self._cell_price(index))
            asyncio.create_task(self._pawn_timeout())
        elif index in getattr(self, "_redeem_cells", []):
            self._pawn_pending = True
            websocket.send_action("unpawn", username=self.config.username,
                                  cell_index=index, value=self._cell_price(index))
            asyncio.create_task(self._pawn_timeout())

    async def _pawn_timeout(self):
        await asyncio.sleep(3)
        if self._pawn_pending:
            self._pawn_pending = False
            self.update()

    def on_pawn_result(self, data: dict):
        """Обрабатывает залог. При оплате долга не оставляем
        активным режим выбора клетки после ответа сервера.
        """
        self._pawn_pending = False
        self._apply_money(data)
        dp = data.get("dict_pawn")
        if dp is not None:
            self.pawned_cells = {int(k) for k, v in dp.items() if v}
        self.apply_ownership_visuals()
        self.update_pawn_visuals()

        if getattr(self, "_payment_mode", False):
            self._pawn_mode = False
            self._sell_mode = False
            self._clear_payment_highlights()
            self._payment_selection = None
            self._set_end_turn_enabled(False)
            self.pawn_wrap.visible = True
            self.sell_wrap.visible = True
        elif self._pawn_mode:
            self._highlight_pawn_cells()

        self._try_repay()
        self.update()

    def on_unpawn_result(self, data: dict):
        """Обрабатывает снятие залога."""
        self._pawn_pending = False
        self._apply_money(data)
        dp = data.get("dict_pawn")
        if dp is not None:
            self.pawned_cells = {int(k) for k, v in dp.items() if v}
        self.apply_ownership_visuals()
        self.update_pawn_visuals()

        if getattr(self, "_payment_mode", False):
            self._pawn_mode = False
            self._sell_mode = False
            self._clear_payment_highlights()
            self._payment_selection = None
            self._set_end_turn_enabled(False)
            self.pawn_wrap.visible = True
            self.sell_wrap.visible = True
        elif self._pawn_mode:
            self._highlight_pawn_cells()

        self._try_repay()
        self.update()

    def _apply_money(self, data: dict):
        self._sync_money(data)

    def _try_repay(self):
        if getattr(self, "_pending_payment", None) is None:
            return
        if self.player_balances.get(self.config.username, 0) >= self._pending_payment:
            pay = self._pending_payment
            self._pending_payment = None
            websocket.send_action("remove_token", username=self.config.username, payments=pay)

    def _cell_price(self, idx):
        name = CELL_DATA.get(idx)
        if name in STREETS_DATA:
            return STREETS_DATA[name].get("price", 0)
        if name in TRANSPORT_DATA:
            return TRANSPORT_DATA[name].get("price", 0)
        if name in UTILITY_DATA:
            return UTILITY_DATA[name].get("price", 0)
        return 0

    def update_pawn_visuals(self):
        if not hasattr(self, '_pawn_blocks'):
            self._pawn_blocks = []
        for b in self._pawn_blocks:
            if b in self.grid_overlay.content.controls:
                self.grid_overlay.content.controls.remove(b)
        self._pawn_blocks.clear()
        board_size = self.height_ - 20
        corner_coef = 1.6
        std_w = board_size / (9 + 2 * corner_coef)
        corner_w = std_w * corner_coef
        for idx in sorted(self.pawned_cells):
            if 0 < idx < 10:
                w, h = std_w, corner_w
                left = board_size - (corner_w + (idx - 1) * std_w) - w
                top = board_size - h
            elif 10 < idx < 20:
                w, h = corner_w, std_w
                left = 0
                top = board_size - (corner_w + (idx - 11) * std_w) - h
            elif 20 < idx < 30:
                w, h = std_w, corner_w
                left = corner_w + (idx - 21) * std_w
                top = 0
            elif 30 < idx < 40:
                w, h = corner_w, std_w
                left = board_size - w
                top = corner_w + (idx - 31) * std_w
            else:
                continue
            card = ft.Container(
                left=left + 2, top=top + 2,
                width=w - 4, height=h - 4,
                bgcolor="#D32F2FDD",
                border=ft.Border.all(2, "#7F0000"),
                border_radius=6,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        ft.Icon(ft.Icons.GAVEL, color="white", size=14),
                        ft.Text("ЗАЛОЖЕНО", size=8, weight=ft.FontWeight.W_900,
                                color="white", max_lines=1,
                                overflow=ft.TextOverflow.CLIP),
                    ],
                    spacing=2, tight=True,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            )
            self._pawn_blocks.append(card)
            self.grid_overlay.content.controls.insert(0, card)
        self.grid_overlay.update()

    async def show_pawned_message(self, cell_name: str):
        card = ft.Container(
            width=450,
            bgcolor="white",
            border_radius=16,
            border=ft.Border.all(4, "#7F0000"),
            padding=ft.Padding.all(25),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color="#44000000"),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(ft.Icons.GAVEL, color="#D32F2F", size=44),
                    ft.Text(cell_name.upper(), size=18, weight=ft.FontWeight.BOLD,
                            color="#234746", text_align=ft.TextAlign.CENTER),
                    ft.Text("УЛИЦА В ЗАЛОГЕ", size=22, weight=ft.FontWeight.W_900, color="#D32F2F"),
                    ft.Text("Арента не взимается", size=14, color="#666666"),
                ],
            ),
        )
        overlay = ft.Container(content=card, expand=True, bgcolor="#88000000",
                               alignment=ft.Alignment.CENTER)
        main_stack = self.controls[0]
        main_stack.controls.append(overlay)
        self.update()
        if self.page:
            self.page.update()
        await asyncio.sleep(2.5)
        if overlay in main_stack.controls:
            main_stack.controls.remove(overlay)
        self.update()
        if self.page:
            self.page.update()

    async def on_bankrupt(self, username: str, creditor: str | None = None):
        await self.on_player_left(username, True, creditor)

    async def on_player_left(
        self,
        username: str,
        bankrupt: bool = False,
        creditor: str | None = None,
    ):
        """Показывает событие выхода/банкротства ровно 3 секунды.

        ВАЖНО: имущество здесь НЕ удаляется и НЕ обнуляется. Источник истины
        по собственности — серверный update_ownership, который после карточки
        либо запускает аукцион, либо передаёт имущество кредитору.
        """
        self._left_players.add(username)

        if bankrupt and creditor:
            title = "ИГРОК ОБАНКРОТИЛСЯ"
            subtitle = f"Имущество и деньги переходят игроку {creditor}"
            color = "#D32F2F"
            icon = ft.Icons.GROUP_OFF
        elif bankrupt:
            title = "БАНКРОТСТВО БАНКУ"
            subtitle = "Имущество уходит в банк"
            color = "#D32F2F"
            icon = ft.Icons.WARNING_AMBER_ROUNDED
        else:
            title = "ИГРОК ВЫШЕЛ ИЗ ИГРЫ"
            subtitle = "Имущество уходит в банк"
            color = "#234746"
            icon = ft.Icons.EXIT_TO_APP

        card = ft.Container(
            width=500,
            bgcolor="white",
            border_radius=16,
            border=ft.Border.all(4, color),
            padding=ft.Padding.all(25),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color="#44000000"),
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
                controls=[
                    ft.Icon(icon, color=color, size=46),
                    ft.Text(title, size=23, weight=ft.FontWeight.W_900, color=color),
                    ft.Text(username, size=18, weight=ft.FontWeight.BOLD, color="#234746"),
                    ft.Text(subtitle, size=14, color="#666666", text_align=ft.TextAlign.CENTER),
                ],
            ),
        )

        overlay = ft.Container(
            content=card,
            expand=True,
            bgcolor="#88000000",
            alignment=ft.Alignment.CENTER,
        )
        main_stack = self.controls[0]
        main_stack.controls.append(overlay)
        self.apply_ownership_visuals()
        self.update_pawn_visuals()
        self.update()
        if self.page:
            self.page.update()

        # Не меняем владения/уровни здесь: сервер делает это после этой паузы.
        await asyncio.sleep(3)

        if overlay in main_stack.controls:
            main_stack.controls.remove(overlay)

        # Убираем только фишку и строку игрока из локального UI.
        token = self.player_tokens.get(username)
        if token:
            for cell in self.cells_objects.values():
                cell.remove_token(token)

        if username in self.display_order:
            self.display_order.remove(username)
            self.info_container.content = ft.Column(
                controls=[self.build_player_row(i, name) for i, name in enumerate(self.display_order)],
                tight=True,
                spacing=20,
                horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            )

        self.update()
        if self.page:
            self.page.update()

    def _sync_money(self, data: dict):
        money = data.get("money")
        if money:
            for name, m in money.items():
                self.player_balances[name] = m
            self.config.money = money
        bal = data.get("balance")
        if bal:
            for name, b in bal.items():
                self.player_balance[name] = b
        self.update_balance_display()
        self._try_repay()

    def _try_repay(self):
        pend = getattr(self, "_pending_payment", None)
        if not pend:
            return
        if self.player_balances.get(self.config.username, 0) >= pend.get("amount", 0):
            self._pending_payment = None
            params = {k: v for k, v in pend.items() if k not in ("action", "amount")}
            websocket.send_action(pend["action"], **params)

    async def on_sell_activ(self, data: dict):
        if data.get("username") != self.config.username:
            return

        is_auction_debt = data.get("reason") == "auction"
        if is_auction_debt:
            # Убираем полноэкранное окно аукциона, чтобы кнопки
            # залога и продажи оставались доступными.
            self.close_auction()

        # Режим погашения долга аукциона. Сервер сам завершит
        # оплату после того, как money станет достаточно.
        self._pending_payment = None
        self._payment_mode = is_auction_debt
        self._payment_amount = int(data.get("payments", 0))
        self._payment_selection = None

        if is_auction_debt:
            self._upgrade_mode = False
            self._sell_mode = False
            self._pawn_mode = False
            self._sell_cells = []
            self._pawn_cells = []
            self._redeem_cells = []
            self.roll_button.visible = False
            self._set_end_turn_enabled(False)
            self.upgrade_wrap.visible = False
            self.pawn_wrap.visible = True
            self.sell_wrap.visible = True
            self.update()

        # Карточка остаётся, но для аукциона она НЕ является
        # полноэкранным overlay — иначе она перекрывает кнопки.
        card = ft.Container(
            width=500, bgcolor="white", border_radius=16,
            border=ft.Border.all(4, "#D32F2F"), padding=ft.Padding.all(25),
            shadow=ft.BoxShadow(spread_radius=2, blur_radius=20, color="#44000000"),
            content=ft.Column(
                tight=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10,
                controls=[
                    ft.Icon(ft.Icons.ERROR_OUTLINE, color="#D32F2F", size=44),
                    ft.Text("НЕ ХВАТАЕТ МОНЕТ!", size=22, weight=ft.FontWeight.W_900, color="#D32F2F"),
                    ft.Text(f"Нужно заплатить: {data.get('payments', 0)}", size=16,
                            weight=ft.FontWeight.BOLD, color="#234746"),
                    ft.Text("Продай уровень или заложи имущество —\nоплата спишется автоматически",
                            size=13, color="#666666", text_align=ft.TextAlign.CENTER),
                ],
            ),
        )

        if is_auction_debt:
            # Карточка находится по центру, но сама карточка, а не overlay,
            # занимает место в Stack — поэтому кнопки продажи/залога доступны.
            card_height = 190
            overlay = ft.Container(
                content=card,
                width=500,
                height=card_height,
                top=max(0, (self.height_ - card_height) / 2),
                left=max(0, (self.width - 500) / 2),
            )
        else:
            overlay = ft.Container(
                content=card,
                expand=True,
                bgcolor="#88000000",
                alignment=ft.Alignment.CENTER,
            )

        main_stack = self.controls[0]
        main_stack.controls.append(overlay)
        self.update()
        if self.page:
            self.page.update()

        await asyncio.sleep(4)
        if overlay in main_stack.controls:
            main_stack.controls.remove(overlay)
        self.update()
        if self.page:
            self.page.update()

    def apply_ownership_visuals(self):
        # Удаляем старые полоски из grid_overlay
        if not hasattr(self, '_ownership_blocks'):
            self._ownership_blocks = []
        for block in self._ownership_blocks:
            if block in self.grid_overlay.content.controls:
                self.grid_overlay.content.controls.remove(block)
        self._ownership_blocks.clear()

        board_size = self.height_ - 20
        corner_coef = 1.6
        std_w = board_size / (9 + 2 * corner_coef)
        corner_w = std_w * corner_coef

        strip_thick = 14
        strip_margin = 4  # отступ от краёв ячейки по длинной стороне

        for idx, owner in self.property_owners.items():
            if owner is None:
                continue
            cell = self.cells_objects.get(idx)
            if not cell:
                continue

            color = self.player_border_color.get(owner, "#FFFFFF")
            block = None

            if 0 < idx < 10:
                # НИЖНЯЯ сторона — полоска НАД ячейкой (между ячейкой и центром)
                strip_len = std_w - 2 * strip_margin
                # X: ячейки идут справа налево, cell.right = corner_w + (idx-1)*std_w
                cell_right_edge = corner_w + (idx - 1) * std_w
                cell_left_x = board_size - cell_right_edge - std_w
                x = cell_left_x + strip_margin
                # Y: верхний край нижних ячеек = board_size - corner_w, полоска чуть выше
                y = board_size - corner_w - strip_thick

                block = ft.Container(
                    width=strip_len, height=strip_thick,
                    bgcolor=color, border_radius=3,
                    left=x, top=y,
                )

            elif 10 < idx < 20:
                # ЛЕВАЯ сторона — полоска СПРАВА от ячейки (между ячейкой и центром)
                strip_len = std_w - 2 * strip_margin
                cell_idx = idx - 11
                # X: правый край левых ячеек = corner_w, полоска чуть правее
                x = corner_w
                # Y: ячейки идут снизу вверх
                cell_bottom_edge = corner_w + cell_idx * std_w
                cell_top_y = board_size - cell_bottom_edge - std_w
                y = cell_top_y + strip_margin

                block = ft.Container(
                    width=strip_thick, height=strip_len,
                    bgcolor=color, border_radius=3,
                    left=x, top=y,
                )

            elif 20 < idx < 30:
                # ВЕРХНЯЯ сторона — полоска ПОД ячейкой (между ячейкой и центром)
                strip_len = std_w - 2 * strip_margin
                cell_idx = idx - 21
                x = corner_w + cell_idx * std_w + strip_margin
                # Y: нижний край верхних ячеек = corner_w, полоска чуть ниже
                y = corner_w

                block = ft.Container(
                    width=strip_len, height=strip_thick,
                    bgcolor=color, border_radius=3,
                    left=x, top=y,
                )

            elif 30 < idx < 40:
                # ПРАВАЯ сторона — полоска СЛЕВА от ячейки (между ячейкой и центром)
                strip_len = std_w - 2 * strip_margin
                cell_idx = idx - 31
                # X: левый край правых ячеек = board_size - corner_w, полоска чуть левее
                x = board_size - corner_w - strip_thick
                y = corner_w + cell_idx * std_w + strip_margin

                block = ft.Container(
                    width=strip_thick, height=strip_len,
                    bgcolor=color, border_radius=3,
                    left=x, top=y,
                )

            if block:
                self._ownership_blocks.append(block)
                self.grid_overlay.content.controls.append(block)
        self.grid_overlay.update()
        if getattr(self, "property_levels", None):
            self.update_levels(self.property_levels)



    async def show_rent_animation(self, payer: str, receiver: str, amount: int, cell_name: str):
    
        receiver_color = self.player_border_color.get(receiver, "#234746")
        payer_color = self.player_border_color.get(payer, "#999")
    
        def make_chip(color, name):
            return ft.Row(
                controls=[
                    ft.Container(
                        content=ft.Container(
                            bgcolor=color,
                            shape=ft.BoxShape.CIRCLE,
                            margin=2,
                        ),
                        width=24, height=24,
                        shape=ft.BoxShape.CIRCLE,
                        border=ft.Border.all(2.5, color),
                    ),
                    ft.Text(name, size=18, weight=ft.FontWeight.BOLD, color="#234746"),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=8,
            )
    
        card = ft.Container(
            width=550, # Сделали карточку шире для горизонтального контента
            bgcolor="white",
            border_radius=16,
            border=ft.Border.all(3, receiver_color),
            padding=ft.Padding.all(30),
            shadow=ft.BoxShadow(
                spread_radius=2,
                blur_radius=20,
                color="#44000000",
            ),
            content=ft.Column(
                tight=True, # Важно! Убирает вертикальное растягивание (как на скриншоте)
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    # Заголовок
                    ft.Text("ОПЛАТА РЕНТЫ", size=14, weight=ft.FontWeight.BOLD, color="#999999", text_align=ft.TextAlign.CENTER),
                    ft.Text(cell_name.upper(), size=22, weight=ft.FontWeight.BOLD, color="#234746", text_align=ft.TextAlign.CENTER),
                    
                    ft.Container(height=20), # Отступ
                    
                    # Горизонтальный блок: Плательщик -> Стрелка -> Получатель
                    ft.Row(
                        alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            # От кого (Слева)
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    make_chip(payer_color, payer),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=6,
                                        controls=[
                                            ft.Text(f"–{amount}", size=32, weight=ft.FontWeight.BOLD, color="#D32F2F"),
                                            ft.Image(src=ECO_COIN_LOGO, width=30, height=30, fit=ft.BoxFit.CONTAIN),
                                        ]
                                    )
                                ]
                            ),
                            
                            # Направление (Стрелка посередине)
                            ft.Icon(ft.Icons.ARROW_FORWARD_ROUNDED, color="#234746", size=45),
                            
                            # Кому (Справа)
                            ft.Column(
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=10,
                                controls=[
                                    make_chip(receiver_color, receiver),
                                    ft.Row(
                                        alignment=ft.MainAxisAlignment.CENTER,
                                        spacing=6,
                                        controls=[
                                            ft.Text(f"+{amount}", size=32, weight=ft.FontWeight.BOLD, color="#2E7D32"),
                                            ft.Image(src=ECO_COIN_LOGO, width=30, height=30, fit=ft.BoxFit.CONTAIN),
                                        ]
                                    )
                                ]
                            ),
                        ]
                    )
                ]
            )
        )
    
        rent_overlay = ft.Container(
            content=card,
            expand=True,
            bgcolor="#88000000",
            alignment=ft.Alignment.CENTER,
            opacity=1,
        )
    
        # Добавляем ПОВЕРХ ВСЕГО — в самый конец стека
        main_stack = self.controls[0]
        main_stack.controls.append(rent_overlay)
        self.update()
        if self.page:
            self.page.update()
    
        await asyncio.sleep(3) # Чуть увеличил тайминг (с 3 до 3.5), чтобы глаза успели прочитать горизонтальный текст
    
        if rent_overlay in main_stack.controls:
            main_stack.controls.remove(rent_overlay)
        self.update()
        if self.page:
            self.page.update()



    def update_balance_display(self):
        """Обновляет только цифры баланса, НЕ трогая имена и порядок"""
        controls = self.info_container.content.controls
        for i, name in enumerate(self.display_order):   # ← используем ФИКСИРОВАННЫЙ порядок
            if i >= len(controls):
                break
            try:
                balance_container = controls[i].content.controls[1]
                balance_row = balance_container.content
                balance_text = balance_row.controls[1]
                balance_text.value = f"{self.player_balances.get(name, 0)}"
            except (IndexError, AttributeError):
                pass
        self.info_container.update()


    async def buy_property(self, cell_index: int, price: int):
        """Покупка собственности"""
        websocket.send_action(
            'buy_property',
            username=self.config.username,
            cell_index=cell_index,
            price=price
        )
        # Закрываем карточку
        self.card_layer.visible = False
        self.card_layer.content = None
        self.pending_purchase_cell = None
        self.update()

    def _refresh_auction_history(self):
        """Обновляет отображение истории ставок."""
        if not self._auction_history_column:
            return
        self._auction_history_column.controls.clear()
        for username, bid in self._auction_history[-6:]:   # последние 6 ставок
            color = self.player_border_color.get(username, "#234746")
            self._auction_history_column.controls.append(
                ft.Container(
                    content=ft.Row(
                        [
                            ft.Icon(ft.Icons.CIRCLE, size=12, color=color),
                            ft.Text(username, size=13, weight=ft.FontWeight.W_500),
                            ft.Text("—", size=13),
                            ft.Text(str(bid), size=13, weight=ft.FontWeight.BOLD),
                            ft.Image(src=ECO_COIN_LOGO, width=14, height=14),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    padding=ft.Padding.symmetric(horizontal=8, vertical=2),
                    bgcolor="#FFFFFFAA" if len(self._auction_history_column.controls) % 2 == 0 else "#F9F9F9",
                    border_radius=6,
                )
            )
        self._auction_history_column.update()

    def _reset_auction_timer(self, is_initiator: bool):
        if self._auction_timer_task:
            self._auction_timer_task.cancel()

        self._auction_time_left = 5

        if self._auction_timer_text:
            self._auction_timer_text.value = f"{self._auction_time_left} сек"
            self._auction_timer_text.color = "#D32F2F"
            self._auction_timer_text.update()

        async def timer_loop():
            try:
                while self._auction_time_left > 0:
                    await asyncio.sleep(1)
                    self._auction_time_left -= 1
                    if self._auction_timer_text:
                        self._auction_timer_text.value = f"{self._auction_time_left} сек"
                        self._auction_timer_text.update()

                if is_initiator:
                    await self._send_auction_end()
            except asyncio.CancelledError:
                pass

        self._auction_timer_task = asyncio.create_task(timer_loop())

    def _build_auction_buttons(self, current_bid: int, current_leader: str | None = None):
        my_balance = self.player_balance.get(self.config.username, 0)

        # Левая кнопка = следующая сотня
        if current_bid < 100:
            left_bid = 100
        else:
            left_bid = ((current_bid // 100) + 1) * 100
        if left_bid - current_bid < 10:
            left_bid += 100

        # Правая кнопка = +25
        right_bid = current_bid + 10

        i_am_leader = current_leader == self.config.username
        can_left = my_balance >= left_bid and left_bid > current_bid and not i_am_leader
        can_right = my_balance >= right_bid and right_bid > current_bid and not i_am_leader

        self._auction_left_btn_text = ft.Text(
            str(left_bid),
            size=16,
            weight=ft.FontWeight.BOLD,
            color="white"
        )

        self._auction_right_btn_text = ft.Text(
            f"{right_bid}",
            size=16,
            weight=ft.FontWeight.BOLD,
            color="white"
        )

        self._auction_left_btn = ft.Button(
            content=ft.Row(
                [
                    self._auction_left_btn_text,
                    ft.Image(src=ECO_COIN_LOGO, width=18, height=18),
                ],
                spacing=6,
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            disabled=not can_left,
            on_click=lambda e: websocket.send_action(
                "auction_bid",
                username=self.config.username,
                bid_amount=left_bid,
            ) if can_left else None,
            style=ft.ButtonStyle(
                bgcolor={
                    "": "#234746" if can_left else "#9E9E9E",
                    ft.ControlState.HOVERED: "#1b3837" if can_left else "#9E9E9E",
                    ft.ControlState.DISABLED: "#9E9E9E",
                },
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            ),
        )

        self._auction_right_btn = ft.Button(
            content=ft.Row(
                [
                    self._auction_right_btn_text,
                    ft.Image(src=ECO_COIN_LOGO, width=18, height=18),
                ],
                spacing=6,
                tight=True,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            disabled=not can_right,
            on_click=lambda e: websocket.send_action(
                "auction_bid",
                username=self.config.username,
                bid_amount=right_bid,
            ) if can_right else None,
            style=ft.ButtonStyle(
                bgcolor={
                    "": "#FF8C00" if can_right else "#9E9E9E",
                    ft.ControlState.HOVERED: "#E65100" if can_right else "#9E9E9E",
                    ft.ControlState.DISABLED: "#9E9E9E",
                },
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=20, vertical=12),
            ),
        )

        return ft.Row(
            [self._auction_left_btn, self._auction_right_btn],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=16,
        )
    

    def update_auction_buttons(self, current_bid: int, current_leader: str | None = None):
        if not self._auction_left_btn or not self._auction_right_btn:
            return

        my_balance = self.player_balance.get(self.config.username, 0)

        if current_bid < 100:
            left_bid = 100
        else:
            left_bid = ((current_bid // 100) + 1) * 100
        if left_bid - current_bid < 10:
            left_bid += 100

        right_bid = current_bid + 10

        i_am_leader = current_leader == self.config.username
        can_left = my_balance >= left_bid and left_bid > current_bid and not i_am_leader
        can_right = my_balance >= right_bid and right_bid > current_bid and not i_am_leader

        self._auction_left_btn_text.value = str(left_bid)
        self._auction_right_btn_text.value = f"{right_bid}"

        self._auction_left_btn.disabled = not can_left
        self._auction_right_btn.disabled = not can_right

        self._auction_left_btn.on_click = lambda e: websocket.send_action(
            "auction_bid",
            username=self.config.username,
            bid_amount=left_bid,
        ) if can_left else None

        self._auction_right_btn.on_click = lambda e: websocket.send_action(
            "auction_bid",
            username=self.config.username,
            bid_amount=right_bid,
        ) if can_right else None

        self._auction_left_btn.style.bgcolor = {
            "": "#234746" if can_left else "#9E9E9E",
            ft.ControlState.HOVERED: "#1b3837" if can_left else "#9E9E9E",
            ft.ControlState.DISABLED: "#9E9E9E",
        }

        self._auction_right_btn.style.bgcolor = {
            "": "#FF8C00" if can_right else "#9E9E9E",
            ft.ControlState.HOVERED: "#E65100" if can_right else "#9E9E9E",
            ft.ControlState.DISABLED: "#9E9E9E",
        }

        self._auction_left_btn.update()
        self._auction_right_btn.update()


    def _build_auction_property_card(self, cell_index: int, cell_name: str, current_bid: int, current_leader: str | None = None):
        # ===== ТРАНСПОРТ =====
        if cell_index in TRANSPORT_INDICES:
            data = TRANSPORT_DATA.get(cell_name)
            if not data:
                return ft.Container()
            rent = data["rent"]

            return ft.Container(
                width=300,
                padding=10,
                bgcolor="white",
                border_radius=10,
                border=ft.Border.all(2, "black"),
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(ft.Icons.DIRECTIONS_BOAT, size=36, color="white"),
                                ft.Text(
                                    cell_name.upper(),
                                    size=14,
                                    weight="bold",
                                    color="white",
                                    text_align=ft.TextAlign.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4),
                            bgcolor="#444444",
                            padding=ft.Padding.all(10),
                            width=280,
                            border=ft.Border.all(2, "black"),
                        ),
                        ft.Container(height=10),
                        self._build_rent_row("1 транспортная компания", rent[0]),
                        self._build_rent_row("2 транспортные компании", rent[1]),
                        self._build_rent_row("3 транспортные компании", rent[2]),
                        self._build_rent_row("4 транспортные компании", rent[3], is_bold=True),
                        ft.Divider(height=20, thickness=2, color="black"),
                        self._build_rent_row("Стоимость покупки", data["price"], is_small=True),
                        self._build_rent_row("Залоговая стоимость", data["mortgage"], is_small=True),
                        self._build_auction_buttons(current_bid, current_leader),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    tight=True,
                ),
            )

        # ===== КОММУНАЛКА =====
        if cell_index in UTILITY_INDICES:
            data = UTILITY_DATA.get(cell_name)
            if not data:
                return ft.Container()
            mult = data["multiplier"]

            return ft.Container(
                width=300,
                padding=10,
                bgcolor="white",
                border_radius=10,
                border=ft.Border.all(2, "black"),
                content=ft.Column(
                    [
                        ft.Container(
                            content=ft.Column([
                                ft.Icon(
                                    ft.Icons.WIND_POWER if "Ветряная" in cell_name else ft.Icons.WATER_DROP,
                                    size=36,
                                    color="white"
                                ),
                                ft.Text(
                                    cell_name.upper(),
                                    size=14,
                                    weight="bold",
                                    color="white",
                                    text_align=ft.TextAlign.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=4),
                            bgcolor="#2E7D32",
                            padding=ft.Padding.all(10),
                            width=280,
                            border=ft.Border.all(2, "black"),
                        ),
                        ft.Container(height=10),
                        ft.Container(
                            content=ft.Text(
                                "Если у вас ОДНО предприятие —\nрента = сумма кубиков × множитель",
                                size=12,
                                color="#234746",
                                text_align=ft.TextAlign.CENTER
                            ),
                            padding=ft.Padding.symmetric(horizontal=10),
                        ),
                        ft.Container(height=5),
                        self._build_rent_row("1 предприятие", f"×{mult[0]}", use_logo=False),
                        self._build_rent_row("2 предприятия", f"×{mult[1]}", use_logo=False, is_bold=True),
                        ft.Divider(height=20, thickness=2, color="black"),
                        self._build_rent_row("Стоимость покупки", data["price"], is_small=True),
                        self._build_rent_row("Залоговая стоимость", data["mortgage"], is_small=True),
                        self._build_auction_buttons(current_bid, current_leader),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=0,
                    tight=True,
                ),
            )

        # ===== УЛИЦЫ =====
        group_color = CELL_COLORS.get(cell_index, "#00000000")
        rent_data = get_card_info(cell_name)
        if rent_data is None:
            return ft.Container()

        rent = rent_data["rent"]
        text_color = "#000000"

        return ft.Container(
            width=300,
            padding=10,
            bgcolor="white",
            border_radius=10,
            border=ft.Border.all(2, "black"),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text("ПРАВО СОБСТВЕННОСТИ", size=10, weight="bold", color=text_color),
                                ft.Text(
                                    rent_data["название"],
                                    size=18,
                                    weight="bold",
                                    color=text_color,
                                    text_align=ft.TextAlign.CENTER
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            spacing=2,
                        ),
                        bgcolor=group_color,
                        padding=ft.Padding.all(10),
                        width=280,
                        border=ft.Border.all(2, "black"),
                    ),
                    ft.Container(height=10),
                    self._build_rent_row("Плата за просто улицу", rent[0], is_bold=True),
                    ft.Divider(height=10, thickness=1, color="#EEEEEE"),
                    self._build_rent_row("С 1 уровнем развития", rent[1]),
                    self._build_rent_row("С 2 уровнями развития", rent[2]),
                    self._build_rent_row("С 3 уровнями развития", rent[3]),
                    self._build_rent_row("С 4 уровнями развития", rent[4]),
                    ft.Container(height=5),
                    self._build_rent_row("УРОВЕНЬ 5 ", rent[5], is_bold=True),
                    ft.Divider(height=20, thickness=2, color="black"),
                    self._build_rent_row("Стоимость покупки", rent_data["цена"], is_small=True),
                    self._build_rent_row("Залоговая стоимость", int(int(rent_data["цена"]) * 0.5), is_small=True),
                    self._build_rent_row("Стоимость уровня", rent_data["star"], is_small=True),
                    self._build_auction_buttons(current_bid, current_leader),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=0,
                tight=True,
            ),
        )



    def update_auction_ui(self, current_bid: int, current_leader: str | None, time_left: int | None = None):
        self._auction_state["current_bid"] = current_bid
        self._auction_state["current_leader"] = current_leader

        if self._auction_bid_text:
            self._auction_bid_text.value = str(current_bid)

        if self._auction_leader_text:
            self._auction_leader_text.value = current_leader if current_leader else "—"

        if time_left is not None:
            self._auction_time_left = time_left
            if self._auction_timer_text:
                self._auction_timer_text.value = f"{time_left} сек" if current_leader else "Ждём ставку"
                self._auction_timer_text.color = "#D32F2F" if current_leader else "#666666"

        self.update_auction_buttons(current_bid, current_leader)

        if self._auction_bid_text:
            self._auction_bid_text.update()
        if self._auction_leader_text:
            self._auction_leader_text.update()
        if self._auction_timer_text:
            self._auction_timer_text.update()

        self.update()
        if self.page:
            self.page.update()



    async def show_eco_quest_dialog(self, data: dict):
        username = data.get("username")
        question_text = data.get("question")
        options = data.get("options", [])
    
        if self._eco_quest_overlay:
            self.close_eco_quest_overlay()
    
        self._eco_selected_index = None
        self._eco_answer_sent = False
        self._eco_buttons = []
        self._eco_correct_index = None
    
        question_card = ft.Container(
            width=550,
            bgcolor="white",
            border_radius=16,
            border=ft.Border.all(3, self.player_border_color.get(username, "#234746")),
            padding=30,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    ft.Text("🌿 ЭКО-КВЕСТ", size=18, weight=ft.FontWeight.BOLD, color="#2E7D32"),
                    ft.Text(f"Отвечает: {username}", size=14, color="#666666"),
                    ft.Divider(height=20, thickness=1, color="#DDDDDD"),
                    ft.Text(question_text, size=16, weight=ft.FontWeight.W_500,
                            text_align=ft.TextAlign.CENTER, color="#234746"),
                    ft.Container(height=20),
                ]
            )
        )
    
        for i, opt in enumerate(options):
            btn = self._build_quest_option_button(i, opt, username == self.config.username)
            self._eco_buttons.append(btn)
            question_card.content.controls.append(btn)
    
        self._eco_quest_overlay = ft.Container(
            content=question_card,
            expand=True,
            bgcolor="#88000000",
            alignment=ft.Alignment.CENTER,
        )
    
        main_stack = self.controls[0]
        main_stack.controls.append(self._eco_quest_overlay)
        self.update()
        if self.page:
            self.page.update()
    
    def _build_quest_option_button(self, index: int, option_text: str, enabled: bool):
        return ft.Button(
            content=ft.Text(
                option_text,
                size=14,
                weight=ft.FontWeight.BOLD,
                color="white",
                text_align=ft.TextAlign.CENTER
            ),
            disabled=not enabled,
            on_click=lambda e: self._on_eco_option_click(index, enabled) if enabled else None,
            style=ft.ButtonStyle(
                bgcolor={
                    "": "#234746",
                    ft.ControlState.HOVERED: "#1b3837",
                    ft.ControlState.DISABLED: "#9E9E9E",
                },
                shape=ft.RoundedRectangleBorder(radius=8),
                padding=ft.Padding.symmetric(horizontal=15, vertical=10),
            ),
            width=500,
        )
    
    def _on_eco_option_click(self, index: int, enabled: bool):
        if not enabled or self._eco_answer_sent:
            return
    
        self._eco_selected_index = index
        self._eco_answer_sent = True
    
        # Блокируем все кнопки и подсвечиваем выбранную
        for i, btn in enumerate(self._eco_buttons):
            btn.disabled = True
            if i == index:
                btn.style = ft.ButtonStyle(
                    bgcolor={"": "#234746", ft.ControlState.HOVERED: "#1b3837"},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                    side=ft.BorderSide(3, self.player_border_color.get(self.config.username, "#234746")),
                )
            else:
                btn.style = ft.ButtonStyle(
                    bgcolor={"": "#9E9E9E"},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                )
            btn.update()
    
        websocket.send_action("eco_quest_answer", username=self.config.username, answer_index=index)
    
    def on_eco_quest_selected(self, data: dict):
        """Вызывается у всех игроков, когда отвечающий выбрал вариант."""
        username = data.get("username")
        selected_index = data.get("selected_index")
    
        if not self._eco_buttons:
            return
    
        # Подсвечиваем выбранную кнопку для всех
        for i, btn in enumerate(self._eco_buttons):
            btn.disabled = True
            if i == selected_index:
                btn.style = ft.ButtonStyle(
                    bgcolor={"": "#234746"},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                    side=ft.BorderSide(3, self.player_border_color.get(username, "#234746")),
                )
            else:
                btn.style = ft.ButtonStyle(
                    bgcolor={"": "#9E9E9E"},
                    shape=ft.RoundedRectangleBorder(radius=8),
                    padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                )
            btn.update()
    
    async def show_eco_quest_result(self, data: dict):
        username = data.get("username")
        correct = data.get("correct", False)
        reward = data.get("reward", 0)
        explanation = data.get("explanation", "")
        money_dict = data.get("money")
        selected_index = data.get("selected_index")
        correct_index = data.get("correct_index")
    
        self._sync_money(data)
    
        # Подсветка результата (поверх уже выбранного)
        if self._eco_quest_overlay and self._eco_buttons:
            for i, btn in enumerate(self._eco_buttons):
                if i == correct_index:
                    btn.style = ft.ButtonStyle(
                        bgcolor={"": "#2E7D32"},
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                        side=ft.BorderSide(3, "#2E7D32"),
                    )
                elif i == selected_index and not correct:
                    btn.style = ft.ButtonStyle(
                        bgcolor={"": "#D32F2F"},
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                        side=ft.BorderSide(3, "#D32F2F"),
                    )
                else:
                    btn.style = ft.ButtonStyle(
                        bgcolor={"": "#9E9E9E"},
                        shape=ft.RoundedRectangleBorder(radius=8),
                        padding=ft.Padding.symmetric(horizontal=15, vertical=10),
                    )
                btn.update()
    
        # Карточка результата
        color = "#2E7D32" if correct else "#D32F2F"
        icon = ft.Icon(ft.Icons.CHECK_CIRCLE if correct else ft.Icons.ERROR, color=color, size=48)
    
        result_card = ft.Container(
            width=500,
            bgcolor="white",
            border_radius=16,
            border=ft.Border.all(3, self.player_border_color.get(username, "#234746")),
            padding=30,
            content=ft.Column(
                tight=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                controls=[
                    icon,
                    ft.Text("ПРАВИЛЬНО!" if correct else "НЕПРАВИЛЬНО!",
                            size=20, weight=ft.FontWeight.BOLD, color=color),
                    ft.Text(f"{username} {f'+{reward}' if correct else f'{reward}'} экокоин(ов)",
                            size=16, color="#234746"),
                    ft.Container(height=10),
                    ft.Text(explanation, size=14, text_align=ft.TextAlign.CENTER, color="#555555"),
                ]
            )
        )
    
        self.close_eco_quest_overlay()
    
        self._eco_quest_overlay = ft.Container(
            content=result_card,
            expand=True,
            bgcolor="#88000000",
            alignment=ft.Alignment.CENTER,
        )
        main_stack = self.controls[0]
        main_stack.controls.append(self._eco_quest_overlay)
        self.update()
        if self.page:
            self.page.update()
    
        await asyncio.sleep(5)
    
        self.close_eco_quest_overlay()
    
    def on_eco_quest_finished(self, username: str):
        if username == self.config.username:
            self.end_turn_button.visible = True
            self.update()
    
    def close_eco_quest_overlay(self):
        if self._eco_quest_overlay:
            main_stack = self.controls[0]
            if self._eco_quest_overlay in main_stack.controls:
                main_stack.controls.remove(self._eco_quest_overlay)
            self._eco_quest_overlay = None
            self.update()