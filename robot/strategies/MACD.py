import numpy as np
import pandas as pd
from robot.client import invest_client, request_iterator
from robot.get_data import ticker_table
from robot import utils
import asyncio


class MovingAverageStrategy:

    def __init__(self, ticker, *, lma=26, sma=12, ama=9):
        self.lots = None
        self.ticker = ticker
        self.client = invest_client
        self.lot = ticker_table[ticker].lot
        self.lma = lma
        self.sma = sma
        self.ama = ama

    async def setup(self):
        await self.client.ainit()
        self.data = await self.client.get_1m_candles(self.ticker, nmins=60)
        self.data = pd.DataFrame(self.data)['close']

        self.subscription = self.client.client.market_data_stream.market_data_stream(
            request_iterator(self.ticker)
        )

        self.long_ma = utils.ema(self.data, self.lma)
        self.short_ma = utils.ema(self.data, self.sma)
        self.macd = self.short_ma - self.long_ma
        self.signal = utils.ema(self.macd, self.ama)

    async def trade(self):
        self.pos = await self.client.get_position(self.ticker)

        if self.pos is None:
            self.lots = 0
        else:
            self.lots = utils.qtof(self.pos.quantity_lots)

        self.balance = await self.client.get_rubs()

        new_value = None
        while (new_value := (await anext(self.subscription)).candle) is None:
            await asyncio.sleep(1)

        new_value = utils.process_candle(new_value)['close']

        new_lma = utils.ema_new_val(new_value, self.long_ma.iloc[-1], self.lma)
        new_sma = utils.ema_new_val(new_value, self.short_ma.iloc[-1], self.sma)
        new_macd = new_sma - new_lma
        new_signal = utils.ema_new_val(new_macd, self.signal.iloc[-1], self.ama)

        ordr = None
        if self.macd.iloc[-1] < self.signal.iloc[-1] and new_macd > new_signal:
            q = (self.balance // new_value) // self.lot
            ordr = await self.client.buy(self.ticker, q)
        elif self.macd.iloc[-1] > self.signal.iloc[-1] and new_macd < new_signal:
            if self.lots > 0:
                ordr = await self.client.sell(self.ticker, self.lots)

        # if ordr is not None:
        #     db.new_entry()

        self.long_ma = np.append(self.long_ma, new_lma)
        self.short_ma = np.append(self.short_ma, new_sma)
        self.macd = np.append(self.macd, new_macd)
        self.signal = np.append(self.signal, new_signal)

