import requests as req
import pandas as pd
from datetime import datetime
from ta.volatility import AverageTrueRange
from ta.trend import EMAIndicator


class Exchange:
    def __init__(self):
        self.api_key = "mx0vglJH419oaT9sT1"

        self.BASE_URL = "https://api.mexc.com"
        self.URL_GET_AVERAGE_PRICE = "/api/v3/avgPrice"
        self.URL_GET_CURRENT_PRICE = "/api/v3/ticker/price"
        self.URL_GET_KLINES = "/api/v3/klines"
        self.URL_GET_SYMBOLS = "/api/v3/defaultSymbols"
        self.URL_GET_SERVER_TIME = "/api/v3/time"

    def get_server_time(self):
        url = self.BASE_URL + self.URL_GET_SERVER_TIME
        headers = {
            "Content-Type": "application/json",
            "X-MEXC-APIKEY": self.api_key
        }
        response = req.get(url, headers=headers)
        if response.status_code != 200:
            return None
        response = response.json()
        return datetime.fromtimestamp(response['serverTime']/1000)

    def get_klines(self, symbol: str, interval: str = "1d", limit: int = 500):
        url = self.BASE_URL + self.URL_GET_KLINES
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        headers = {
            "Content-Type": "application/json",
            "X-MEXC-APIKEY": self.api_key
        }
        response = req.get(url, params=params, headers=headers)
        if response.status_code != 200:
            return None
        return response.json()

    def get_symbols(self):
        url = self.BASE_URL + self.URL_GET_SYMBOLS
        headers = {
            "Content-Type": "application/json",
            "X-MEXC-APIKEY": self.api_key
        }
        response = req.get(url, headers=headers).json()
        return response["data"]

    def analyze_and_plot_old(self, symbol: str, interval: str = "1d"):
        data = self.get_klines(symbol, interval)
        for i in data:
            # i[0] = int(i[0])
            # i[6] = int(i[6])
            i[7] = float(i[7])
            i[1] = float(i[1])
            i[2] = float(i[2])
            i[3] = float(i[3])
            i[4] = float(i[4])
            i[5] = float(i[5])
            df = pd.DataFrame(data, columns=['Open time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Close time',
                                             'Quote asset volume'])

            df['Open time'] = pd.to_datetime(df['Open time'], unit='ms')

            df['Close'] = df['Close'].astype(float)

            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()

            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))

            df['Upperband'] = df['SMA_50'] + (df['Close'].rolling(window=20).std() * 2)
            df['Lowerband'] = df['SMA_50'] - (df['Close'].rolling(window=20).std() * 2)

            def trading_strategy(row):
                if row['Close'] < row['Lowerband']:
                    return 'long'
                elif row['Close'] > row['Upperband']:
                    return 'short'
                return 'hold'

            df['Signal'] = df.apply(trading_strategy, axis=1)

            def set_stop_loss_take_profit(row, stop_loss_pct=0.02, take_profit_pct=0.05):
                if row['Signal'] == 'long':
                    stop_loss = row['Close'] * (1 - stop_loss_pct)
                    take_profit = row['Close'] * (1 + take_profit_pct)
                elif row['Signal'] == 'short':
                    stop_loss = row['Close'] * (1 + stop_loss_pct)
                    take_profit = row['Close'] * (1 - take_profit_pct)
                else:
                    stop_loss, take_profit = None, None
                return pd.Series([stop_loss, take_profit])

            df[['Stop Loss', 'Take Profit']] = df.apply(set_stop_loss_take_profit, axis=1)

            long_signals = df[df['Signal'] == 'long']
            short_signals = df[df['Signal'] == 'short']

            return long_signals, short_signals

    async def analyze_and_plot(self, symbol: str, interval: str = "1d"):
        data = self.get_klines(symbol, interval)
        df_data = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_asset_volume'
        ])
        df_data[['open', 'high', 'low', 'close']] = df_data[['open', 'high', 'low', 'close']].astype(float)

        long_signals, short_signals = self.UT_Bot_Alerts(df_data, key_value=2, atr_period=10, use_heikin_ashi=False)

        return long_signals, short_signals

    def UT_Bot_Alerts(self, data, key_value=1, atr_period=10, use_heikin_ashi=False):
        """
        Implements UT Bot Alerts in Python.

        Parameters:
            data (DataFrame): OHLC data with columns ['open', 'high', 'low', 'close'].
            key_value (float): Multiplier to adjust sensitivity.
            atr_period (int): Period for ATR calculation.
            use_heikin_ashi (bool): Whether to use Heikin Ashi candles for signals.

        Returns:
            DataFrame: DataFrame with buy/sell signals and trailing stop levels.
        """
        df = data.copy()

        # Calculate Heikin Ashi candles if enabled
        if use_heikin_ashi:
            df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
            src = df['ha_close']
        else:
            src = df['close']

        # Calculate ATR
        atr = AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=atr_period)
        df['atr'] = atr.average_true_range()
        n_loss = key_value * df['atr']

        # Initialize trailing stop
        df['xATRTrailingStop'] = 0.0
        for i in range(1, len(df)):
            if src[i] > df.loc[i - 1, 'xATRTrailingStop'] and src[i - 1] > df.loc[i - 1, 'xATRTrailingStop']:
                df.loc[i, 'xATRTrailingStop'] = max(df.loc[i - 1, 'xATRTrailingStop'], src[i] - n_loss[i])
            elif src[i] < df.loc[i - 1, 'xATRTrailingStop'] and src[i - 1] < df.loc[i - 1, 'xATRTrailingStop']:
                df.loc[i, 'xATRTrailingStop'] = min(df.loc[i - 1, 'xATRTrailingStop'], src[i] + n_loss[i])
            else:
                df.loc[i, 'xATRTrailingStop'] = src[i] - n_loss[i] if src[i] > df.loc[i - 1, 'xATRTrailingStop'] else \
                src[
                    i] + \
                n_loss[
                    i]

        # Determine positions
        df['pos'] = 0
        for i in range(1, len(df)):
            if src[i - 1] < df.loc[i - 1, 'xATRTrailingStop'] and src[i] > df.loc[i - 1, 'xATRTrailingStop']:
                df.loc[i, 'pos'] = 1
            elif src[i - 1] > df.loc[i - 1, 'xATRTrailingStop'] and src[i] < df.loc[i - 1, 'xATRTrailingStop']:
                df.loc[i, 'pos'] = -1
            else:
                df.loc[i, 'pos'] = df.loc[i - 1, 'pos']

        # Generate buy/sell signals
        df['buy'] = (src > df['xATRTrailingStop']) & (src.shift(1) <= df['xATRTrailingStop'].shift(1))
        df['sell'] = (src < df['xATRTrailingStop']) & (src.shift(1) >= df['xATRTrailingStop'].shift(1))

        buys = df[df['buy']].copy()
        sells = df[df['sell']].copy()

        return buys, sells

