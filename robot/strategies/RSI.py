import asyncio
import numpy as np
import pandas as pd

from robot.client import invest_client, request_iterator
from robot.get_data import ticker_table
from robot import utils

import talib


class RelativeStrengthIndicatorStrategy:

    def __init__(self, ticker, *, rsi_param=14, rsi_low=20, rsi_high=80, interval=None):
        self.lots = None
        self.ticker = ticker
        self.client = invest_client
        self.lot = ticker_table[ticker].lot
        self.rsi_param = rsi_param
        self.rsi_low = rsi_low
        self.rsi_high = rsi_high
        self.interval = interval

    async def setup(self, time: dict = None):

        await self.client.ainit()

        self.df = await self.client.get_candles(self.ticker, self.interval, time)
        self.df = pd.DataFrame(self.df)[['time', 'close']]
        self.df['rsi'] = talib.RSI(self.df['close'], timeperiod=self.rsi_param)

        self.subscription = self.client.client.market_data_stream.market_data_stream(request_iterator(self.ticker))

    async def trade(self):
        self.pos = await self.client.get_position(self.ticker)

        if self.pos is None:
            self.lots = 0
        else:
            self.lots = utils.qtof(self.pos.quantity_lots)

        self.balance = await self.client.get_rubs()

        new_candle = None
        while (new_candle := (await anext(self.subscription)).candle) is None:
            await asyncio.sleep(2)

        new_row = utils.process_candle(new_candle)

        if new_row['time'] == self.df.iloc[-1].time:
            return None

        # REFACTORING NEEDED
        self.df.loc[len(self.df)] = pd.Series(
            {'time': new_row['time'], 'close': new_row['close'], 'rsi': pd.NA})
        self.df['rsi'] = talib.RSI(self.df['close'], timeperiod=self.rsi_param)
        print(self.df.tail())

        if self.df.rsi.iloc[-1] >= self.rsi_high:
            if self.lots > 0:
                await self.client.sell(self.ticker, self.lots)
        elif self.df.rsi.iloc[-1] <= self.rsi_low:
            q = (self.balance // self.df.close.iloc[-1]) // self.lot
            await self.client.buy(self.ticker, int(q))
