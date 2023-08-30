import numpy as np

from db import db
from robot import candles, order
from robot import get_data, utils


class MovingAverageStrategy:

    def __init__(self, ticker, client, *, lma=26, sma=12, ama=9):
        self.lots = None
        self.ticker = ticker
        self.client = client
        self.lot = get_data.ticker_table[ticker].lot
        self.lma = lma
        self.sma = sma
        self.ama = ama

    def setup(self, data):
        self.data = data
        self.subscription = self.client.market_data_stream.market_data_stream(
            candles.request_iterator(self.ticker)
        )

        self.long_ma = utils.ema(data, self.lma)
        self.short_ma = utils.ema(data, self.sma)
        self.macd = self.short_ma - self.long_ma
        self.signal = utils.ema(self.macd, self.ama)

    async def trade(self):
        self.pos = await order.get_pos(self.ticker, self.client)
        self.lots = utils.qtof(self.pos.quantity_pos)
        self.balance = await order.get_balance(self.client)
        new_value = anext(self.subscription)

        new_lma = utils.ema_new_val(new_value, self.long_ma[-1], self.lma)
        new_sma = utils.ema_new_val(new_value, self.short_ma[-1], self.sma)
        new_macd = new_sma - new_lma
        new_signal = utils.ema_new_val(new_macd, self.signal[-1], self.ama)

        ordr = None
        if self.macd[-1] < self.signal and new_macd > new_signal:
            q = (self.balance // new_value) // self.lot
            ordr = await order.buy(self.ticker, q, self.client)
        elif self.macd[-1] > self.signal and new_macd < new_signal:
            if self.lots > 0:
                ordr = await order.sell(self.ticker, self.lots, self.client)

        # if ordr is not None:
        #     db.new_entry()

        self.long_ma = np.append(self.long_ma, new_lma)
        self.short_ma = np.append(self.short_ma, new_sma)
        self.macd = np.append(self.macd, new_macd)
        self.signal = np.append(self.signal, new_signal)



