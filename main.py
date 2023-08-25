import asyncio

import pandas as pd
from tinkoff.invest import AsyncClient

import candles
import finmath
import order
from load_settings import settings

import matplotlib.pyplot as plt

TOKEN = settings.token
ACCOUNT_ID = settings.account_id
TICKER = 'RUAL'
# MVID RUAL SBER VTBR VKCO


async def main():
    async with AsyncClient(TOKEN) as client:
        cndls = await candles.get_1m_candles(TICKER, client, nmins=60)
        cndl_it = client.market_data_stream.market_data_stream(candles.request_iterator(TICKER))
        df = pd.DataFrame(cndls).set_index('time').close
        while True:
            lst = await anext(cndl_it)
            lst = await candles.process_candle(lst.candle)
            if lst is None:
                continue

            df.loc[lst['time']] = lst['close']

            lng = finmath.moving_average(df, 26)
            shrt = finmath.moving_average(df, 12)
            lng = finmath.moving_average(lng, 9)
            shrt = finmath.moving_average(shrt, 9)

            if lng.iloc[-2].item() > shrt.iloc[-2].item() and lng.iloc[-1].item() < shrt.iloc[-1].item():
                await order.buy(TICKER, 2, client)
                await asyncio.sleep(30)
                print('sold')

            if lng.iloc[-2].item() < shrt.iloc[-2].item() and lng.iloc[-1].item() > shrt.iloc[-1].item():
                await order.sell(TICKER, 2, client)
                await asyncio.sleep(30)
                print('bought')


if __name__ == "__main__":
    asyncio.run(main())
