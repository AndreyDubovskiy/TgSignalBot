from db.controllers.BalancesController import BalancesController
from db.models.BalanceModel import BalanceModel

from utils.Exchange import Exchange
from datetime import datetime
import asyncio

class Balancer:
    def __init__(self):
        self.balances_controller = BalancesController()
        asyncio.run(self.all_delete())
        self.exchange = Exchange()

    async def get(self, name: str, timeframe: str) -> BalanceModel:
        tmp = await self.balances_controller.get_by(name=name, timeframe=timeframe)
        if len(tmp) == 0:
            buys, sells = await self.exchange.analyze_and_plot(symbol=name, interval=timeframe)
            buy = buys.iloc[-1]
            buy_time = datetime.fromtimestamp(int(buy['close_time'])/1000)
            sell = sells.iloc[-1]
            sell_time = datetime.fromtimestamp(int(sell['close_time'])/1000)

            if sell_time > buy_time:
                signal_price = buy['close']
                signal_type = 'buy'
                signal_time = buy_time
            else:
                signal_price = sell['close']
                signal_type = 'sell'
                signal_time = sell_time

            await self.balances_controller.create(name=name, timeframe=timeframe, signal_price=signal_price, signal_type=signal_type, updated_at=signal_time, created_at=signal_time)
            tmp = await self.balances_controller.get_by(name=name, timeframe=timeframe)
            return tmp[0]
        else:
            return tmp[0]

    async def all_delete(self):
        await self.balances_controller.delete_all()
