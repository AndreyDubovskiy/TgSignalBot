import asyncio
import config_controller
from telebot.async_telebot import AsyncTeleBot
from db.controllers.UsersController import UsersController
from db.controllers.SubscribesController import SubscribesController
from utils.Exchange import Exchange
from datetime import datetime, timedelta
from logger.MyLogger import Logger
from utils.Balancer import Balancer
import time
import requests as req

class MsgSender:
    def __init__(self, token: str = config_controller.TOKEN_BOT):
        self.token = token
        print("TOKEN", self.token)
        self.url = f"https://api.telegram.org/bot{self.token}/"
        self.headers = {"Content-Type": "application/json"}

    def send(self, text: str, chat_id: str, parse_mode: str = None):
        url = self.url + "sendMessage"
        data = {"chat_id": chat_id, "text": text}
        if parse_mode is not None:
            data["parse_mode"] = parse_mode
            data["link_preview_options"] = {"is_disabled": True}
        response = req.post(url, json=data, headers=self.headers)
        if response.status_code != 200:
            return False
        return True








class SenderSignal:
    def __init__(self):
        self.msg_sender = MsgSender()
        self.user_controller = UsersController()
        self.subscribe_controller = SubscribesController()
        self.exchange = Exchange()
        self.last_time_tick = time.time()
        self.count_time = 0
        #self.logger = Logger(filename="SenderSignal",
        #                     write_in_file=True,
        #                     add_time=True,
        #                     write_in_console=False)

    async def tick(self):
        print("LAST TIME TICK", time.time() - self.last_time_tick)
        self.last_time_tick = time.time()
        time_start_tick = time.time()
        balancer = Balancer()
        await balancer.all_delete()
        subscribes_list = await self.subscribe_controller.get_all()
        current_datatime = self.exchange.get_server_time()
        for subscribe in subscribes_list:
            try:
                delta_time = None
                if subscribe.timeframe == "1m":
                    delta_time = timedelta(minutes=1)
                elif subscribe.timeframe == "5m":
                    delta_time = timedelta(minutes=5)
                elif subscribe.timeframe == "15m":
                    delta_time = timedelta(minutes=15)
                elif subscribe.timeframe == "30m":
                    delta_time = timedelta(minutes=30)
                elif subscribe.timeframe == "60m":
                    delta_time = timedelta(minutes=60)
                elif subscribe.timeframe == "4h":
                    delta_time = timedelta(hours=4)
                elif subscribe.timeframe == "1d":
                    delta_time = timedelta(days=1)
                elif subscribe.timeframe == "1W":
                    delta_time = timedelta(days=7)
                elif subscribe.timeframe == "1M":
                    delta_time = timedelta(days=30)
                else:
                    delta_time = timedelta(days=1)

                if (current_datatime - subscribe.updated_at) >= delta_time:
                    #longs, shorts = self.exchange.analyze_and_plot(subscribe.symbol, subscribe.timeframe)
                    signal_obj = await balancer.get(name=subscribe.symbol, timeframe=subscribe.timeframe)

                    # long = longs.iloc[-1]
                    # short = shorts.iloc[-1]
                    # long_time = datetime.fromtimestamp(long['Close time'] / 1000)
                    # short_time = datetime.fromtimestamp(short['Close time'] / 1000)
                    if signal_obj.signal_type == 'buy':
                        if signal_obj.updated_at > subscribe.updated_at:
                            sum_tmp = (await self.subscribe_controller.get_by(id=subscribe.id))[0]
                            sum_tmp.updated_at = current_datatime
                            await self.subscribe_controller.save(sum_tmp)

                            user = (await self.user_controller.get_by(id=subscribe.user_id))[0]
                            if config_controller.IS_AFTER_SIGNAL:
                                self.msg_sender.send(text=f"🟢 LONG\n"
                                                                        f"Пара: {subscribe.symbol}\n"
                                                                        f"Таймфрейм: {subscribe.timeframe}\n"
                                                                        f"Ціна: {signal_obj.signal_price}\n"
                                                                        f"Час: {(signal_obj.updated_at+timedelta(hours=2))}\n" + config_controller.AFTER_SIGNAL_TEXT,
                                                                        chat_id=user.tg_id, parse_mode="HTML")
                            else:
                                self.msg_sender.send(text=f"🟢 LONG\n"
                                                          f"Пара: {subscribe.symbol}\n"
                                                          f"Таймфрейм: {subscribe.timeframe}\n"
                                                          f"Ціна: {signal_obj.signal_price}\n"
                                                          f"Час: {(signal_obj.updated_at + timedelta(hours=2))}",
                                                     chat_id=user.tg_id)

                            # await self.bot.send_message(user.tg_id, f"🟢 LONG\n"
                            #                                         f"Пара: {subscribe.symbol}\n"
                            #                                         f"Таймфрейм: {subscribe.timeframe}\n"
                            #                                         f"Ціна: {signal_obj.signal_price}\n"
                            #                                         f"Час: {(signal_obj.updated_at+timedelta(hours=2))}")
                            #self.logger.log(f"LONG {subscribe.timeframe}",
                            #                long)

                    else:
                        if signal_obj.updated_at > subscribe.updated_at:
                            sum_tmp = (await self.subscribe_controller.get_by(id=subscribe.id))[0]
                            sum_tmp.updated_at = current_datatime
                            await self.subscribe_controller.save(sum_tmp)

                            user = (await self.user_controller.get_by(id=subscribe.user_id))[0]
                            if config_controller.IS_AFTER_SIGNAL:
                                self.msg_sender.send(text=f"🔴 SHORT\n"
                                                                        f"Пара: {subscribe.symbol}\n"
                                                                        f"Таймфрейм: {subscribe.timeframe}\n"
                                                                        f"Ціна: {signal_obj.signal_price}\n"
                                                                        f"Час: {(signal_obj.updated_at+timedelta(hours=2))}\n" + config_controller.AFTER_SIGNAL_TEXT,
                                                                        chat_id=user.tg_id, parse_mode="HTML")
                            else:
                                self.msg_sender.send(text=f"🔴 SHORT\n"
                                                          f"Пара: {subscribe.symbol}\n"
                                                          f"Таймфрейм: {subscribe.timeframe}\n"
                                                          f"Ціна: {signal_obj.signal_price}\n"
                                                          f"Час: {(signal_obj.updated_at + timedelta(hours=2))}",
                                                     chat_id=user.tg_id)
                            # await self.bot.send_message(user.tg_id, f"🔴 SHORT\n"
                            #                                         f"Пара: {subscribe.symbol}\n"
                            #                                         f"Таймфрейм: {subscribe.timeframe}\n"
                            #                                         f"Ціна: {signal_obj.signal_price}\n"
                            #                                         f"Час: {(signal_obj.updated_at+timedelta(hours=2))}")
                            #self.logger.log(f"SHORT {subscribe.timeframe}",
                            #                short)

            except Exception as ex:
                print(ex)
                #self.logger.log(f"ERROR",
                 #               ex)
        end_time_tick = time.time()
        time_tick = end_time_tick - time_start_tick
        self.count_time = time_tick
        print(f"[{datetime.now()}]","TIME FOR TICK", time_tick, " COUNT ", len(subscribes_list))
        #self.logger.log("TIME FOR TICK",
        #                time_tick, " COUNT ", len(subscribes_list))
        #self.logger.save()
