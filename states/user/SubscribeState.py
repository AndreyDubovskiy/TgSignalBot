import markups
from states.template.UserState import UserState
from states.template.Response import Response
from db.controllers.SubscribesController import SubscribesController
from db.controllers.UsersController import UsersController
import config_controller
from utils.Exchange import Exchange
import utils.whitelist as whitelist

class SybscribeState(UserState):
    async def start_msg(self):
        self.subscribe_controller = SubscribesController()
        self.user_controller = UsersController()
        self.exchange = Exchange()
        self.is_whitelist = await whitelist.is_whitelist(self.user_name ,self.user_id)
        if not self.is_whitelist:
            return Response(text="У вас немає дозволу користуватися ботом!", is_end=True)
        self.user_bd = await self.user_controller.get_by(tg_id=self.user_id)
        if len(self.user_bd) == 0:
            await self.user_controller.create(tg_id=self.user_id, tg_name=self.user_name)
            self.user_bd = (await self.user_controller.get_by(tg_id=self.user_id))[0]
        else:
            self.user_bd = self.user_bd[0]
        self.subscribe_list = await self.subscribe_controller.get_by(user_id=self.user_bd.id)

        self.PAGE_MAX = 8
        self.page = 0
        self.is_page = False

        if len(self.subscribe_list) > self.PAGE_MAX:
            self.is_page = True

        self.edit = "None"
        self.current_subscribe = None
        self.current_list_subscribe = await self.subscribe_controller.get_by(user_id=self.user_bd.id, offset=self.page, limit=self.PAGE_MAX)

        return Response(text="Список підписок", buttons=markups.generate_list_subscribes(self.current_list_subscribe, self.is_page), is_end=False)

    async def next_msg(self, message: str):
        if self.edit == "add":
            self.add_symbol = message
            res = self.exchange.get_klines(symbol=self.add_symbol)
            if res == None or len(res) == 0:
                return Response(text="Пара невірна!\n\nВведіть ще раз:", buttons=markups.generate_cancel())
            self.edit = "add_time"
            return Response(text="Виберіть таймфрейм:", buttons=markups.generate_timeframe())



    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            if self.current_subscribe is not None:
                return Response(redirect="/subscribes_list")
            if self.user_id in config_controller.list_is_loggin_admins:
                return Response(redirect="/intro")
            return Response(redirect="/menu")
        elif data_btn == "/next":
            self.page += self.PAGE_MAX
            tmp = await self.subscribe_controller.get_by(user_id=self.user_bd.id, offset=self.page, limit=self.PAGE_MAX)
            if len(tmp) == 0:
                self.page -= self.PAGE_MAX
                return Response(text="Список підписок",
                                buttons=markups.generate_list_subscribes(self.current_list_subscribe, self.is_page),
                                is_end=False)
            else:
                self.current_list_subscribe = tmp
                return Response(text="Список підписок",
                                buttons=markups.generate_list_subscribes(self.current_list_subscribe, self.is_page),
                                is_end=False)

        elif data_btn == "/back":
            self.page -= self.PAGE_MAX
            if self.page < 0:
                self.page = 0
                return Response(text="Список підписок",
                                buttons=markups.generate_list_subscribes(self.current_list_subscribe, self.is_page),
                                is_end=False)
            else:
                self.current_list_subscribe = await self.subscribe_controller.get_by(user_id=self.user_bd.id, offset=self.page, limit=self.PAGE_MAX)
                return Response(text="Список підписок",
                                buttons=markups.generate_list_subscribes(self.current_list_subscribe, self.is_page),
                                is_end=False)

        elif data_btn == "/add":
            self.edit = "add"
            return Response(text="Введіть пару у форматі BTCUSDT:", buttons=markups.generate_cancel())
        elif self.edit == "add_time":
            self.edit = "None"
            await self.subscribe_controller.create(user_id=self.user_bd.id, symbol=self.add_symbol, timeframe=data_btn)
            return Response(text="Підписка створена!", redirect="/subscribes_list")
        elif data_btn == "/delete":
            await self.subscribe_controller.delete(id=int(self.current_subscribe.id))
            return Response(text="Підписка видалена!", redirect="/subscribes_list")
        else:
            self.current_subscribe = (await self.subscribe_controller.get_by(id=int(data_btn)))[0]
            return Response(text=f"[Підписка]\n"
                                 f"Пара: {self.current_subscribe.symbol}\n"
                                 f"Таймфрейм: {self.current_subscribe.timeframe}", buttons=markups.generate_semi_menu_subscribe(), is_end=False)

