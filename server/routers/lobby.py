from fastapi import APIRouter, Query, Form, WebSocket, HTTPException, WebSocketException, status, WebSocketDisconnect
from .instrument import generation_code_lobby, check_code, roll_dice_unique, get_ordered_list
from ..data import Lobby, DICT_LOBBY, get_random_question, CELL_DATA, MORTGAGE_DATA
from .instrument import ConnectionManager
from typing import Annotated
import asyncio


router = APIRouter(tags=["лобби"])
@router.post('/create')
async def create_code_lobby():
    global DICT_LOBBY
    code = generation_code_lobby()
    if code == 503:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
    DICT_LOBBY[code] = Lobby()
    return code

@router.websocket('/ws/connect/{code}')
async def connect_lobby(websocket: WebSocket, code: int):
    global DICT_LOBBY
    if code not in DICT_LOBBY:
        await websocket.close(code=1003)
        return
    
    await websocket.accept()
    msg = await websocket.receive_json()
    username = msg.get("username")
    if not username:
        await websocket.close(code=1003)
        return
    
    lobby = DICT_LOBBY[code]
    DICT_STREET = lobby.DICT_STREET
    DICT_PAWN = lobby.DICT_PAWN
    if len(lobby.usernames) >= 4:
        await websocket.send_json({"type": "error"})
        return
    
    if lobby.ready:
        await websocket.send_json({'type': "server start"})
        return
    
    manager = ConnectionManager(lobby=lobby)
    lobby.usernames = await manager.connect(username, websocket)

    async def _finalize_auction(lobby, manager, auction):
        """Завершает аукцион и передаёт собственность победителю"""
        # Аукцион имущества вышедшего игрока нельзя завершать до первой ставки.
        # Это защищает новый аукцион от старого/запоздалого auction_end.
        if auction.get("is_leaver_auction") and not auction.get("current_leader"):
            return

        auction["active"] = False
        winner = auction.get("current_leader")
        final_bid = auction.get("current_bid", 0)
        cell_index = auction.get("cell_index")
        
        if winner and final_bid >= auction["start_price"] and lobby.balance.get(winner, 0) >= final_bid:
            if lobby.money.get(winner, 0) < final_bid:
                lobby.auction_debt = {
                    "username": winner, "amount": final_bid,
                    "cell_index": cell_index, "cell_name": auction["cell_name"],
                    "initiator": auction.get("initiator"),
                }
                lobby.auction = None
                await manager.broadcast({
                    "type": "sell_activ",
                    "payments": final_bid,
                    "username": winner,
                    "reason": "auction",
                })
                # Запуск следующего аукциона из очереди, если она есть
                if getattr(lobby, "auction_queue", None):
                    await _start_next_leaver_auction()
                return
            # Покупка победителем
            lobby.money[winner] -= final_bid
            lobby.balance[winner] -= final_bid
            lobby.property_owners[cell_index] = winner
            lobby.balance[winner] += MORTGAGE_DATA[cell_index]
            print(f"end auction. username: {winner}, final_bid: {final_bid}, Mortagage_data: {MORTGAGE_DATA[cell_index]}")
            print(f"balance: {lobby.balance}")
            await manager.broadcast({
                "type": "auction_won",
                "winner": winner,
                "final_bid": final_bid,
                "cell_index": cell_index,
                "cell_name": auction["cell_name"],
                "money": lobby.money,
                'balance': lobby.balance
            })
            levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
            await manager.broadcast({
                "type": "update_ownership",
                "owners": {str(k): v for k, v in lobby.property_owners.items()},
                "money": lobby.money,
                "balance": lobby.balance,
                "levels": levels,
                "dict_pawn": DICT_PAWN,
                "player_color": lobby.player_color
            })
        else:
            # Никто не выиграл
            await manager.broadcast({
                "type": "auction_cancelled",
                "cell_index": cell_index,
                "cell_name": auction["cell_name"]
            })
            if lobby.property_owners.get(cell_index) not in lobby.usernames:
                lobby.property_owners[cell_index] = None
                levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
                await manager.broadcast({
                    "type": "update_ownership",
                    "owners": {str(k): v for k, v in lobby.property_owners.items()},
                    "money": lobby.money,
                    "levels": levels,
                    "dict_pawn": DICT_PAWN,
                })
        lobby.auction = None
        # Запуск следующего аукциона из очереди, если она есть
        if getattr(lobby, "auction_queue", None):
            await _start_next_leaver_auction()
    

    async def _try_complete_auction_debt():
        debt = getattr(lobby, "auction_debt", None)
        if not debt:
            return
        u, amount = debt["username"], debt["amount"]
        if lobby.money.get(u, 0) >= amount:
            lobby.money[u] -= amount
            lobby.balance[u] -= int(amount / 2)
            print(f"_try_complete_auction_debt. username: {u}, ammount: {amount}")
            print(f"balance: {lobby.balance}")

            lobby.property_owners[debt["cell_index"]] = u
            lobby.auction_debt = None
            await manager.broadcast({
                "type": "auction_won",
                "winner": u,
                "final_bid": amount,
                "cell_index": debt["cell_index"],
                "cell_name": debt["cell_name"],
                "initiator": debt.get("initiator"),
                "money": lobby.money,
                "balance": lobby.balance,
            })
            levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
            await manager.broadcast({
                "type": "update_ownership",
                "owners": {str(k): v for k, v in lobby.property_owners.items()},
                "money": lobby.money,
                "balance": lobby.balance,
                "levels": levels,
                "dict_pawn": DICT_PAWN,
                "player_color": lobby.player_color
            })
        elif lobby.balance.get(u, 0) < amount:
            lobby.auction_debt = None
            conn = manager.active_connections.get(u)
            if conn:
                raise WebSocketDisconnect(code=1000, reason="bankrupt")


    leaver_auction_timer_task = None

    async def _start_next_leaver_auction():
        nonlocal leaver_auction_timer_task

        if leaver_auction_timer_task and not leaver_auction_timer_task.done():
            leaver_auction_timer_task.cancel()
            leaver_auction_timer_task = None

        queue = getattr(lobby, "auction_queue", None) or []
        if not queue:
            lobby.auction = None
            if lobby.next_user in lobby.usernames:
                await manager.broadcast({
                    "type": "roll_dice",
                    "username_roll": lobby.next_user,
                })
            return

        cell = queue.pop(0)
        lobby.auction = {
            "active": True,
            "cell_index": cell,
            "cell_name": CELL_DATA[cell],
            "start_price": 0,
            "current_bid": 0,
            "current_leader": None,
            "initiator": None,
            "bid_history": [],
            "time_left": 5,
            "is_leaver_auction": True,
        }

        await manager.broadcast({
            "type": "auction_started",
            "cell_index": cell,
            "cell_name": CELL_DATA[cell],
            "start_price": 0,
            "current_bid": 0,
            "current_leader": None,
            "initiator": None,
            "bid_history": [],
            "time_left": 5,
            "is_leaver_auction": True,
        })

        async def _leaver_timer(auction_cell):
            try:
                # ВАЖНО: до первой ставки аукцион не имеет таймера завершения.
                # После первой ставки идёт обычные 5 секунд, и каждая новая ставка
                # снова запускает клиентский таймер с 5 секунд.
                while (
                    getattr(lobby, "auction", None)
                    and lobby.auction.get("cell_index") == auction_cell
                    and lobby.auction.get("active")
                ):
                    if not lobby.auction.get("current_leader"):
                        await asyncio.sleep(0.2)
                        continue

                    await asyncio.sleep(1)
                    if not getattr(lobby, "auction", None):
                        return
                    if lobby.auction.get("cell_index") != auction_cell:
                        return
                    if not lobby.auction.get("active"):
                        return
                    lobby.auction["time_left"] = max(0, lobby.auction.get("time_left", 5) - 1)
                    if lobby.auction["time_left"] <= 0:
                        await _finalize_auction(lobby, manager, lobby.auction)
                        return
            except asyncio.CancelledError:
                pass

        leaver_auction_timer_task = asyncio.create_task(_leaver_timer(cell))


    if msg.get("type") != "join":
        await websocket.close(code=1003)

    if not check_code(code):
        await websocket.close(code=1003)
        return 

    

    async def handle_message(data: dict):
        msg_type = data.get("type")
        username: str = data.get("username")
        
        if msg_type == "ready":
            username_list = list(lobby.usernames.keys())
            if username in username_list:
                id = username_list.index(username)
                if id not in lobby.ready_users:
                    lobby.ready_users.append(id)
                if username not in lobby.player_color:
                    for slot in range(4):
                        if slot not in lobby.player_color.values():
                            lobby.player_color[username] = slot
                            print(lobby.player_color)
                            break
                    
                        
                if (len(lobby.ready_users) == len(lobby.usernames) and 2 <= len(lobby.ready_users) <= 4):
                    lobby.ready = True
                    if not hasattr(lobby, 'property_owners'):
                        lobby.property_owners = {i: None for i in range(40)}
                    username_list = list(lobby.usernames.keys())
                    lobby.next_user = username_list[0]
                    lobby.money = {
                        username: 1500 for username in lobby.usernames.keys()
                    }
                    lobby.balance= lobby.money.copy()
                    await manager.broadcast({'type': "lobby_ready", "usernames": username_list, 'money': lobby.money, 'balance': lobby.balance, "player_color": lobby.player_color})
                    await manager.broadcast({'type': 'roll_dice', "username_roll": username_list[0]})
                else:
                    await manager.broadcast({"type": "give_list", "usernames": username_list, "ready": lobby.ready_users})

        elif msg_type == "add_200":
            lobby.money[username] += 200
            lobby.balance[username] +=200
            await _try_complete_auction_debt()
            levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
            await manager.broadcast({
                "type": "update_ownership",
                "owners": {str(k): v for k, v in lobby.property_owners.items()},
                "money": lobby.money,
                "balance": lobby.balance,
                "levels": levels,
                "dict_pawn": DICT_PAWN,
                "player_color": lobby.player_color
            })

        elif msg_type == "remove_token":
            payments = int(data.get("payments", 0))
            if lobby.money[username] < payments:
                if lobby.balance[username] >= payments:
                    await manager.broadcast({
                        'type': "sell_activ",
                        "payments": payments,
                        "username": username,
                        "reason": "rent",
                    })
                else:
                    raise WebSocketDisconnect(reason="bankrupt")
            else:
                lobby.money[username] -= payments
                lobby.balance[username] -= payments
                print(f"снятие {payments} игроку {username}")
                print(lobby.property_owners.items())
                levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
                await manager.broadcast({
                    "type": "update_ownership",
                    "owners": {str(k): v for k, v in lobby.property_owners.items()},
                    "money": lobby.money,
                    'balance': lobby.balance,
                    "levels" : levels,
                    "dict_pawn": DICT_PAWN,
                })

        elif msg_type == "pawn":
            cell_index = int(data.get("cell_index"))
            value = int(data.get("value"))
            owner = set()
            for k, v in lobby.property_owners.items():
                if v == username:
                    owner.add(k)
            levels = {"5":0,"15":0,"25":0,"35":0,"12":0,"28":0}
            for color, street in DICT_STREET.items():
                for k,v in street.items():
                    levels[str(k)] = v 
            if levels.get(str(cell_index)) is not None:
                if cell_index in owner:
                    if levels.get(str(cell_index)) == 0 and not DICT_PAWN[cell_index]:
                        DICT_PAWN[cell_index] = True
                        lobby.money[username] += int(value/2)
                        print(f"залог: {int(value/2)}")
                        await _try_complete_auction_debt()

            levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
            await manager.broadcast({
                "type": "pawn",
                "cell_index": cell_index,
                "username": username,
                "levels": levels,
                "money": lobby.money,
                'balance': lobby.balance,
                "dict_pawn" : DICT_PAWN,
            })
            return

        elif msg_type == "unpawn":
            cell_index = int(data.get("cell_index"))
            value = int(data.get("value"))
            owner = set()
            for k, v in lobby.property_owners.items():
                if v == username:
                    owner.add(k)
            levels = {"5":0,"15":0,"25":0,"35":0,"12":0,"28":0}
            for color, street in DICT_STREET.items():
                for k,v in street.items():
                    levels[str(k)] = v 
            if levels.get(str(cell_index)) is not None:
                if cell_index in owner and DICT_PAWN[cell_index]:
                    lobby.money[username] -= int(value/2)
                    print(f"разлог: {int(value/2)}")
                    DICT_PAWN[cell_index] = False

            levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
            await manager.broadcast({
                "type": "unpawn",
                "cell_index": cell_index,
                "username": username,
                "levels": levels,
                "money": lobby.money,
                'balance': lobby.balance,
                "dict_pawn" : DICT_PAWN
            }) 
            return
            

            
        elif msg_type == "upgrade_level":
            level_price = int(data.get("level"))
            cell_index = int(data.get("cell_index"))
            owner = set()
            
            for k, v in lobby.property_owners.items():
                if v == username:
                    owner.add(k)
            for color, street in DICT_STREET.items():
                if set(street.keys()).issubset(owner):
                    if street.get(cell_index) is not None:
                        if lobby.money[username] - level_price >= 0:
                            if min(list(street.values())) == street[cell_index] and street[cell_index]<5 and not DICT_PAWN[cell_index]:
                                print("куплен уровень")
                                lobby.money[username] -= level_price
                                lobby.balance[username] -= int(level_price/2)
                                street[cell_index] +=1
                                levels = {str(k): v for color, street in DICT_STREET.items() for k,v in street.items()}
                                await manager.broadcast({
                                    "type": "upgrade_result",
                                    "username": username,
                                    "ok": True,
                                    "levels": levels,
                                    "money": lobby.money,
                                    'balance': lobby.balance,
                                    "dict_pawn": DICT_PAWN
                                })
                                return

            levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
            print("ошибка покупки")
            await manager.broadcast({
                "type": "upgrade_result",
                "username": username,
                "ok": False,
                "levels": levels,
                "money": lobby.money,
                'balance': lobby.balance,
                "dict_pawn": DICT_PAWN
            })

        elif msg_type == "sell_level":
            level_price = int(data.get("level"))
            cell_index = int(data.get("cell_index"))
            owner = set()
            for k, v in lobby.property_owners.items():
                if v == username:
                    owner.add(k)

                for color, street in DICT_STREET.items():
                    if set(street.keys()).issubset(owner):
                        if street.get(cell_index) is not None:
                            if street[cell_index] > 0 and max(list(street.values())) == street[cell_index] and not DICT_PAWN[cell_index]:
                                street[cell_index] -= 1
                                lobby.money[username] += int(level_price / 2)
                                print("минут уровень")
                                await _try_complete_auction_debt() 
                                levels = {str(k):v for color, street in DICT_STREET.items() for k,v in street.items()}
                                await manager.broadcast({
                                    "type": "sell_level",
                                    "username": username,
                                    "ok": True,
                                    "levels": levels,
                                    "money": lobby.money,
                                    'balance': lobby.balance,
                                    "dict_pawn": DICT_PAWN
                                })
                                return
                        
            levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
            await manager.broadcast({
                "type": "sell_level",
                "username": username,
                "ok": False,
                "levels": levels,
                "money": lobby.money,
                'balance': lobby.balance,
                "dict_pawn": DICT_PAWN
            })
            return
                            

        elif msg_type == "dice":
            list_roll_dice = roll_dice_unique(lobby.username_queue)
            print(f"бросок {list_roll_dice}")
            lobby.username_queue[username] = list_roll_dice
            await manager.broadcast({
                "type": "dice",
                "username_roll": username,
                "roll_dice": list_roll_dice
            })

        elif msg_type == "buy_property":
            cell_index = data.get("cell_index")
            username = data.get("username")
            price = data.get("price")
        
            if username != lobby.next_user:
                await websocket.send_json({"type": "buy_failed", "username": username, "reason": "not_your_turn"})
                return
        
            if lobby.property_owners.get(cell_index) is not None:
                await websocket.send_json({"type": "buy_failed", "username": username, "reason": "already_owned"})
                return
        
            username_list = list(lobby.usernames.keys())
        
            
            if lobby.money[username]>=price:
                lobby.money[username] -= price
                lobby.balance[username] -= int(price/2)
                lobby.property_owners[cell_index] = username
            else:
                await websocket.send_json({"type": "buy_failed", "username": username, "reason": "insufficient_funds"})
                return
        
            await manager.broadcast({
                "type": "buy_success",
                "cell_index": cell_index,
                "owner": username
            })
            levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
            print(f"levels {levels}")
            await manager.broadcast({
                "type": "update_ownership",
                "owners": {str(k): v for k, v in lobby.property_owners.items()},
                "money": lobby.money,
                "balance": lobby.balance,
                "levels": levels,
                "dict_pawn": DICT_PAWN,
                "player_color": lobby.player_color
            })

        elif msg_type == "pay_rent":
            cell_index = data.get("cell_index")
            payer = data.get("username")
            owner = data.get("owner")
            amount = data.get("amount")

            if payer != lobby.next_user:
                return

            username_list = list(lobby.usernames.keys())
            if payer not in username_list or owner not in username_list:
                return

            if lobby.property_owners.get(cell_index) != owner:
                return

            payer_idx = username_list.index(payer)
            owner_idx = username_list.index(owner)

            

            amount = int(amount)
            if lobby.money[payer] < amount:
                if lobby.balance[payer] >= amount:
                    await manager.broadcast({
                        'type': "sell_activ",
                        "payments": amount,
                        "username": payer,
                        "reason": "rent",
                    })
                    return
                else:
                    raise WebSocketDisconnect(reason="bankrupt")
            else:
                lobby.money[payer] -= amount
                lobby.balance[payer] -= amount
            
            lobby.money[owner] += amount
            lobby.balance[owner] += amount

            CELL_NAMES = {
                0: "СТАРТ", 1: "Казахская степь", 2: "Эко-квест", 3: "Пампасы Аргентины", 4: "Эко-сбор",
                5: "Северный морской путь", 6: "Река Нил", 7: "Эко-квест", 8: "Река Янцзы", 9: "Река Ганг",
                10: "посетитель", 11: "Джунгли Борнео", 12: "Ветряная электростанция", 13: "Леса Конго", 14: "Леса Амазонии",
                15: "Панамский канал", 16: "Ледники Гренландии", 17: "Эко-квест", 18: "Льды Антарктиды", 19: "Арктический шельф",
                20: "Бесплатный отдых", 21: "Индийский океан", 22: "Эко-квест", 23: "Атлантический океан", 24: "Тихий океан",
                25: "Транссибирская магистраль", 26: "Токио", 27: "Нью-Йорк", 28: "Опреснительная станция", 29: "Шанхай",
                30: "На проверку", 31: "Галапагосские острова", 32: "Озеро Байкал", 33: "Эко-квест", 34: "Большой Барьерный риф",
                35: "Суэцкий канал", 36: "Эко-квест", 37: "Фукусимская зона", 38: "Налог на выбросы CO2", 39: "Чернобыльская зона"
            }

            await manager.broadcast({
                "type": "rent_paid",
                "payer": payer,
                "receiver": owner,
                "amount": amount,
                "cell_name": CELL_NAMES.get(cell_index, ""),
                "money": lobby.money,
                'balance': lobby.balance,
            })

        elif msg_type == "start_auction":
            cell_index = data.get("cell_index")
            username = data.get("username")
            cell_name = data.get("cell_name", "")
            start_price = data.get("start_price", 0)

            if not isinstance(start_price, (int, float)) or start_price < 0:
                start_price = 0

            lobby.auction = {
                "active": True,
                "cell_index": cell_index,
                "cell_name": cell_name,
                "start_price": start_price,
                "current_bid": start_price,
                "current_leader": None,
                "initiator": username,
                "bid_history": [],
            }

            await manager.broadcast({
                "type": "auction_started",
                "cell_index": cell_index,
                "cell_name": cell_name,
                "start_price": start_price,
                "current_bid": start_price,
                "current_leader": None,
                "initiator": username,
                "bid_history": [],
                "time_left": 5
            })


        elif msg_type == "eco_quest_trigger":
            if username != lobby.next_user:
                await websocket.send_json({"type": "error", "message": "Не ваш ход"})
                return

            question = get_random_question()
            if not question:
                await manager.broadcast({
                    "type": "eco_quest_finished",
                    "username": username
                })
                return

            lobby.eco_quest_current = {
                "username": username,
                "question": question,
                "answered": False
            }

            await manager.broadcast({
                "type": "eco_quest_question",
                "username": username,
                "question": question["question"],
                "options": question["options"]
            })

        elif msg_type == "eco_quest_answer":
            answer_index = data.get("answer_index")
            if username != lobby.next_user:
                return
        
            quest = lobby.eco_quest_current
            if not quest or quest["username"] != username or quest.get("answered"):
                return
        
            question = quest["question"]               # ← получаем вопрос здесь
            quest["selected_index"] = answer_index
            quest["answered"] = True
        
            # Рассылаем всем информацию о выборе
            await manager.broadcast({
                "type": "eco_quest_selected",
                "username": username,
                "selected_index": answer_index
            })
            
            # Запускаем отложенную проверку результата
            async def process_quest_result():
                await asyncio.sleep(2)  # пауза для визуального эффекта
                question = quest["question"]
                correct = (answer_index == question["correct_index"])
                reward = 200 if correct else -100
                if reward==200:
                    lobby.money[username] += reward
                    lobby.balance[username] += reward
                else:
                    if lobby.money[username] < reward:
                        if lobby.balance[username] >= reward:
                            await manager.broadcast({
                                'type': "sell_activ",
                                "payments": reward,
                                "username": username,
                                "reason": "rent"
                            })
                            return
                        else:
                            raise WebSocketDisconnect(reason="bankrupt")
                    else:
                        lobby.money[username] += reward
                        lobby.balance[username] += reward
                    
                await _try_complete_auction_debt()
                print("lobby.balance : ", lobby.balance)
        
                explanation = question["explanation"]
                if not correct:
                    explanation = f"Неправильно! {explanation}"
        
                await manager.broadcast({
                    "type": "eco_quest_result",
                    "username": username,
                    "correct": correct,
                    "reward": reward,
                    "explanation": explanation,
                    "money": lobby.money,
                    'balance': lobby.balance,
                    "selected_index": answer_index,
                    "correct_index": question["correct_index"]
                })
        
                await manager.broadcast({
                    "type": "eco_quest_finished",
                    "username": username
                })
        
            asyncio.create_task(process_quest_result())

        elif msg_type == "auction_bid":
            username = data.get("username")
            bid_amount = data.get("bid_amount", 0)
            
            auction = getattr(lobby, 'auction', None)
            if not auction or not auction.get("active"):
                return
            
            # Проверки
            if bid_amount <= auction["current_bid"]:
                await websocket.send_json({"type": "auction_error", "message": "Ставка должна быть выше"})
                return
            if lobby.balance.get(username, 0) < bid_amount:
                await websocket.send_json({"type": "auction_error", "message": "Недостаточно средств"})
                return
            
            # Обновление
            auction["current_bid"] = bid_amount
            auction["current_leader"] = username
            auction["last_bid_time"] = asyncio.get_event_loop().time()
            auction["bid_history"].append((username, bid_amount))
            auction["time_left"] = 5
            
            await manager.broadcast({
                "type": "auction_update",
                "current_bid": bid_amount,
                "current_leader": username,
                "bid_history": auction["bid_history"][-10:],
                "time_left": 5,  # сброс таймера
                "message": f"{username} предлагает {bid_amount}!"
            })

        elif msg_type == "auction_end":
            username = data.get("username")
            auction = getattr(lobby, 'auction', None)
            if not auction or not auction.get("active"):
                return

            if auction.get("is_leaver_auction"):
                return

            initiator = auction.get("initiator")
            if not initiator or username != initiator:
                return

            await _finalize_auction(lobby, manager, auction)

        



        elif msg_type == "end_turn":
            username_list = list(lobby.usernames.keys())

            if lobby.start:
                if username not in lobby.end_turn_users:
                    lobby.end_turn_users.append(username)

                current_idx = username_list.index(username)
                next_idx = (current_idx + 1) % len(username_list)
                next_user = username_list[next_idx]

                await manager.broadcast({
                    'type': 'roll_dice',
                    "username_roll": next_user
                })

                if len(lobby.end_turn_users) == len(lobby.usernames):
                    ordered_players = get_ordered_list(lobby.username_queue, username_list)
                    lobby.usernames = {name: lobby.usernames[name] for name in ordered_players}
                    lobby.start = False
                    lobby.username_queue.clear()
                    lobby.end_turn_users.clear()
                    lobby.next_user = ordered_players[0]

                    await manager.broadcast({
                        "type": "start",
                        "usernames": list(lobby.usernames.keys()),
                        "money": lobby.money,
                        'balance': lobby.balance
                    })
                    levels = {str(k):v for colors, street in DICT_STREET.items() for k,v in street.items()}
                    await manager.broadcast({
                        "type": "update_ownership",
                        "owners": {str(k): v for k, v in lobby.property_owners.items()},
                        "money": lobby.money,
                        "balance": lobby.balance,
                        "levels": levels,
                        "dict_pawn": DICT_PAWN,
                        "player_color": lobby.player_color
                    })
                    await manager.broadcast({
                        "type": "roll_dice",
                        "username_roll": ordered_players[0],
                    })
            else:
                current_idx = username_list.index(username)
                next_idx = (current_idx + 1) % len(username_list)
                lobby.next_user = username_list[next_idx]

                await manager.broadcast({
                    'type': 'roll_dice',
                    "username_roll": lobby.next_user
                })
    try:
        await manager.broadcast({"type": "give_list", "usernames": list(lobby.usernames.keys()), "ready" : lobby.ready_users})
    
        while True:
            data = await websocket.receive_json()
            await handle_message(data)

    except WebSocketDisconnect as e:
        reason = e.reason or ""
        bankrupt = reason.startswith("bankrupt")
        creditor = reason.split(":", 1)[1] if ":" in reason else None
        if creditor and creditor not in lobby.usernames:
            creditor = None 
        if bankrupt:
            await manager.broadcast({"type": "bankrupt", "username": username, "creditor": creditor})
        else:
            await manager.broadcast({"type": "exit", "username": username})

        await asyncio.sleep(3)  
        was_active = (username == lobby.next_user)
        lobby.usernames = manager.disconnect(username)
        if username in lobby.username_queue:
            del lobby.username_queue[username]
        
        owner_cells = [k for k, v in lobby.property_owners.items() if v == username]
        
        if bankrupt and creditor and creditor in lobby.usernames:
            
            for cell in owner_cells:
                lobby.property_owners[cell] = creditor
            lobby.money[creditor] = lobby.money.get(creditor, 0) + lobby.money.get(username, 0)
            lobby.balance[creditor] = lobby.balance.get(creditor, 0) + lobby.balance.get(username, 0)
        else:
           
            for cell in owner_cells:
                lobby.property_owners[cell] = None
               
                for street in DICT_STREET.values():
                    if cell in street:
                        street[cell] = 0
                DICT_PAWN[cell] = False 

        lobby.player_color.pop(username, None)

        lobby.money.pop(username, None)
        lobby.balance.pop(username, None)   
        
        levels = {str(k): v for color, street in DICT_STREET.items() for k, v in street.items()}
        await manager.broadcast({
            "type": "update_ownership",
            "owners": {str(k): v for k, v in lobby.property_owners.items()},
            "money": lobby.money,
            "balance": lobby.balance,
            "levels": levels,
            "dict_pawn": DICT_PAWN,
            "player_color": lobby.player_color
        })  
        
        remaining_users = list(lobby.usernames.keys())
        if len(remaining_users) > 0:
            if was_active:
                lobby.next_user = remaining_users[0] 
                await manager.broadcast({'type': 'roll_dice', "username_roll": lobby.next_user})
            await manager.broadcast({"type": "give_list", "usernames": remaining_users, "ready": lobby.ready_users})
            
            if len(remaining_users) == 1 and lobby.ready:
                await manager.broadcast({"type": "win", "username": remaining_users[0]})
                await asyncio.sleep(30)
                await manager.broadcast({'type': 'delete'})
                if code in DICT_LOBBY:
                    del DICT_LOBBY[code]
        else:
           
            if code in DICT_LOBBY:
                del DICT_LOBBY[code]

    except Exception as e:
        await websocket.close(code=1011)