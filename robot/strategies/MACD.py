import asyncio
import numpy as np
import pandas as pd

from robot.client import invest_client, request_iterator
from robot.get_data import ticker_table
from robot import utils

import talib


class MovingAverageStrategy:

    def __init__(self, ticker, *, lma=26, sma=12, ama=9, interval=None):
        self.lots = None
        self.ticker = ticker
        self.client = invest_client
        self.lot = ticker_table[ticker].lot
        self.lma = lma
        self.sma = sma
        self.ama = ama
        self.interval = interval

    async def setup(self, time: dict = None):

        await self.client.ainit()

        self.df = await self.client.get_candles(self.ticker, self.interval, time)
        self.df = pd.DataFrame(self.df)[['time', 'close']]
        self.df['macd'], self.df['signal'], macdhist = talib.MACD(self.df['close'], slowperiod=self.lma,
                                                                  fastperiod=self.sma, signalperiod=self.ama)

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
            {'time': new_row['time'], 'close': new_row['close'], 'macd': pd.NA, 'signal': pd.NA})
        self.df['macd'], self.df['signal'], macdhist = talib.MACD(self.df['close'], slowperiod=self.lma,
                                                                  fastperiod=self.sma, signalperiod=self.ama)

        if self.df.macd.iloc[-2] < self.df.signal.iloc[-2] and self.df.macd.iloc[-1] > self.df.signal.iloc[-1]:
            q = (self.balance // self.df.close.iloc[-1]) // self.lot
            await self.client.buy(self.ticker, int(q))
        elif self.df.macd.iloc[-2] > self.df.signal.iloc[-2] and self.df.macd.iloc[-1] < self.df.signal.iloc[-1]:
            if self.lots > 0:
                await self.client.sell(self.ticker, self.lots)
