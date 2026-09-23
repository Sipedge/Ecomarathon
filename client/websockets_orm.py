import asyncio
import json
import websockets
from data import Config
import utils
from alerts import AlertDialog_spawn

class WebSocketClient:
    def __init__(self):
        self.websocket = None
        self.msg_queue = asyncio.Queue()
        self.listen_task = None
        self.process_task = None
        self.page = None

    async def connect(self, config: Config, page):
        self.page = page
        try:
            self.websocket = await websockets.connect(
                f"{config.ws_domen}/lobby/ws/connect/{config.code}"
            )
            await self.websocket.send(json.dumps({
                "type": "join",
                "username": config.username
            }))
            self.listen_task = asyncio.create_task(self._listen())
            self.process_task = asyncio.create_task(self._process_messages(config))
        except Exception as e:
            config._errors = f"Не удалось подключиться."

    async def _listen(self):
        try:
            async for message in self.websocket:
                data = json.loads(message)
                await self.msg_queue.put(data)
        except Exception as e:
            pass

    async def _process_messages(self, config):
        while True:
            data: dict = await self.msg_queue.get()
            type_ = data.get("type")
            print(f"type: {data.get("type", None)}, username: {data.get("username",None)}, money: {data.get("maney", None)}, balance: {data.get('balance')}")

            if type_ == 'error':
                if utils.lobby:
                    await utils.lobby.lobby_full()
                if utils.game:
                    await utils.game.close()
                return
            
            if type_ == "eco_quest_selected":
                if utils.game:
                    utils.game.on_eco_quest_selected(data)
            

            if type_ == "eco_quest_question":
                if utils.game:
                    asyncio.create_task(utils.game.show_eco_quest_dialog(data))

            if type_ == "eco_quest_result":
                if utils.game:
                    await utils.game.show_eco_quest_result(data)

            if type_ == "eco_quest_finished":
                if utils.game:
                    utils.game.on_eco_quest_finished(data.get("username"))


            if type_ == "buy_success":
                if utils.game:
                    owner = data.get("owner")
                    cell_index = data.get("cell_index")
                    if owner == config.username:
                        utils.game.end_turn_button.visible = True
                        utils.game.update()

            if type_ == "win":
                if utils.game:
                    await utils.game.winner(data)

            if type_ == "server start":
                if utils.lobby:
                    await utils.lobby.alert_await()
                if utils.game:
                    await utils.game.close()
                return

            if type_ == "update_ownership":
                if utils.game:
                    owners = data.get("owners", {})
                    money_dict = data.get("money")
                    utils.game.update_ownership(data.get("owners", {}), data.get("money"), data.get("levels"), data.get("dict_pawn"), data.get("balance"))

            if type_ == "auction_started":
                if utils.game:
                    asyncio.create_task(utils.game.show_auction_dialog(
                        cell_index=data.get("cell_index"),
                        cell_name=data.get("cell_name", ""),
                        start_price=data.get("start_price", 0),
                        current_bid=data.get("current_bid", 10),
                        current_leader=data.get("current_leader"),
                        initiator=data.get("initiator"),
                        bid_history=data.get("bid_history", []),
                        time_left=data.get("time_left", 5),
                        is_initiator=(data.get("initiator") == config.username),
                    ))

            if type_ == "auction_update":
                if utils.game:
                    utils.game.on_auction_update(
                        current_bid=data.get("current_bid", 0),
                        current_leader=data.get("current_leader", ""),
                        bid_history=data.get("bid_history", []),
                        time_left=data.get("time_left", 5),
                    )

            if type_ == "auction_won":
                if utils.game:
                    winner = data.get("winner")
                    final_bid = data.get("final_bid")
                    cell_index = data.get("cell_index")
                    await utils.game.on_auction_won(winner, final_bid, cell_index, config.username, data.get("initiator"))

            if type_ == "auction_cancelled":
                if utils.game:
                    utils.game.close_auction()
                    if config.username == utils.game._auction_initiator:
                        utils.game.end_turn_button.visible = True
                        utils.game.update()

            if type_ == "sell_level":
                if utils.game:
                    utils.game.on_sell_result(data)
            if type_ == "unpawn":
                if utils.game:
                    utils.game.on_unpawn_result(data)
                    
            if type_ == "bankrupt":
                if utils.game:
                    asyncio.create_task(utils.game.on_player_left(
                        data.get("username"),
                        True,
                        data.get("creditor"),
                    ))
                if data.get("username") == config.username:
                    if utils.lobby:
                        await utils.lobby.alert_bancrut()
                return

            if type_ == "exit":
                username =  data.get("username", None)
                if utils.game and username!=config.username:
                    asyncio.create_task(utils.game.on_player_left(
                        data.get("username"),
                        False,
                        None,
                    ))

                if username == config.username:
                    if utils.game:
                        await utils.game.close()
                return
                
            if type_ == "sell_activ":
                if utils.game:
                    asyncio.create_task(utils.game.on_sell_activ(data))
            if type_ == "pawn":
                if utils.game:
                    utils.game.on_pawn_result(data)
            if type_ == "upgrade_result":
                utils.game.on_upgrade_result(data)

            if type_ == "rent_paid":
                if utils.game:
                    payer = data.get("payer")
                    receiver = data.get("receiver")
                    amount = data.get("amount")
                    cell_name = data.get("cell_name", "")
                    money_dict = data.get("money")
                    
                    if money_dict:
                        utils.game.player_balances = money_dict.copy()
                        utils.game.update_balance_display()

                    await utils.game.show_rent_animation(payer, receiver, amount, cell_name)

                    if payer == config.username:
                        utils.game.end_turn_button.visible = True
                        utils.game.update()

            if type_ == "buy_failed":
                if utils.game:
                    reason = data.get("reason", "")
                    failed_user = data.get("username", "")
                    print(f"[BUY_FAILED] user={failed_user}, reason={reason}")
                   
                    if failed_user == config.username:
                        utils.game.card_layer.visible = False
                        utils.game.card_layer.content = None
                        utils.game.end_turn_button.visible = True
                        utils.game.update()

            if type_ == "give_list":
                usernames = data.get("usernames", [])
                if utils.game:
                    await utils.game.update_players_list(usernames)
                if utils.lobby:
                    utils.lobby.update_users(usernames, data.get("ready", []))

            if type_ == "start":
                config.usernames = data.get('usernames')
                config.money = data.get('money')
                if utils.game:
                    utils.game.is_rolling_phase = False
                    await utils.game.update_players_list(config.usernames)

            if type_ == "lobby_ready":
                config.usernames = data.get('usernames')
                config.money = data.get('money')
                if utils.lobby:
                    await utils.lobby.start()
                if utils.game:
                    await utils.game.update_players_list(config.usernames)

            if type_ == "roll_dice":
                if utils.game:
                    await utils.game.update_roll_dice_button(data)

            if type_ == "dice":
                if utils.game:
                    username = data.get("username_roll")
                    list_roll_dice = data.get('roll_dice')
                    await utils.game.roll_dice_container(username, list_roll_dice)

            if type_ == "delete":
                if utils.game:
                    await utils.game.close()

            self.msg_queue.task_done()



    def send_action(self, action_type: str, **kwargs):
        if not self.websocket:
            return
        
        msg = {"type": action_type, **kwargs}
        asyncio.create_task(self.websocket.send(json.dumps(msg)))

    async def close(self, config: Config):
        config.code = 0
        utils.lobby = None
        utils.game = None
        
        while not self.msg_queue.empty():
            try:
                self.msg_queue.get_nowait()
            except asyncio.QueueEmpty:
                break  

        if self.listen_task:
            self.listen_task.cancel()
        if self.process_task:
            self.process_task.cancel()
        if self.websocket:
            await self.websocket.close()
        


websocket = WebSocketClient()