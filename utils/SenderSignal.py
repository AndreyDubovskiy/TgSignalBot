import asyncio
from telebot.async_telebot import AsyncTeleBot
from db.controllers.UsersController import UsersController
from db.controllers.SubscribesController import SubscribesController
from utils.Exchange import Exchange
from datetime import datetime, timedelta
from logger.MyLogger import Logger
from utils.Balancer import Balancer
import time


class SenderSignal:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot
        self.user_controller = UsersController()
        self.subscribe_controller = SubscribesController()
        self.exchange = Exchange()
        #self.logger = Logger(filename="SenderSignal",
        #                     write_in_file=True,
        #                     add_time=True,
        #                     write_in_console=False)

    async def tick(self):
        print("TICK START")
        time_start_tick = time.time()
        balancer = Balancer()
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
                            await self.bot.send_message(user.tg_id, f"🟢 LONG\n"
                                                                    f"Пара: {subscribe.symbol}\n"
                                                                    f"Таймфрейм: {subscribe.timeframe}\n"
                                                                    f"Ціна: {signal_obj.signal_price}\n"
                                                                    f"Час: {(signal_obj.updated_at+timedelta(hours=2))}")
                            #self.logger.log(f"LONG {subscribe.timeframe}",
                            #                long)

                    else:
                        if signal_obj.updated_at > subscribe.updated_at:
                            sum_tmp = (await self.subscribe_controller.get_by(id=subscribe.id))[0]
                            sum_tmp.updated_at = current_datatime
                            await self.subscribe_controller.save(sum_tmp)

                            user = (await self.user_controller.get_by(id=subscribe.user_id))[0]
                            await self.bot.send_message(user.tg_id, f"🔴 SHORT\n"
                                                                    f"Пара: {subscribe.symbol}\n"
                                                                    f"Таймфрейм: {subscribe.timeframe}\n"
                                                                    f"Ціна: {signal_obj.signal_price}\n"
                                                                    f"Час: {(signal_obj.updated_at+timedelta(hours=2))}")
                            #self.logger.log(f"SHORT {subscribe.timeframe}",
                            #                short)

            except Exception as ex:
                print(ex)
                #self.logger.log(f"ERROR",
                 #               ex)
        end_time_tick = time.time()
        time_tick = end_time_tick - time_start_tick
        print("TIME FOR TICK", time_tick, " COUNT ", len(subscribes_list))
        #self.logger.log("TIME FOR TICK",
        #                time_tick, " COUNT ", len(subscribes_list))
        #self.logger.save()
