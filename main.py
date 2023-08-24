import asyncio

import pandas as pd
from tinkoff.invest import AsyncClient

import candles
import finmath
import orders
from load_settings import settings

import matplotlib.pyplot as plt

TOKEN = settings.token
ACCOUNT_ID = settings.account_id
TICKER = 'RUAL'


async def main():
    async with AsyncClient(TOKEN) as client:
        try:
            cndls = await candles.get_1m_candles(TICKER, client, nmins=60)
            cndl_it = client.market_data_stream.market_data_stream(candles.request_iterator(TICKER))
            df = pd.DataFrame(cndls).set_index('time').close
            while True:
                lst = await anext(cndl_it)
                lst = await candles.process_candle(lst.candle)
                if lst is None:
                    continue

                df.loc[lst['time']] = lst['close']

                fast = finmath.moving_average(df, 12)
                slow = finmath.moving_average(df, 26)
                fast = finmath.moving_average(fast, 9)
                slow = finmath.moving_average(slow, 9)

                if fast.iloc[-2] > slow.iloc[-2] and fast.iloc[-1] < slow.iloc[-1]:
                    await orders.sell(TICKER, 1, client)
                    print('sold')

                if fast.iloc[-2] < slow.iloc[-2] and fast.iloc[-1] > slow.iloc[-1]:
                    await orders.buy(TICKER, 1, client)
                    print('bought')

                await asyncio.sleep(30)

        except KeyboardInterrupt:
            pass
        # finally:
        #     await client.cancel_all_orders(account_id=ACCOUNT_ID)


if __name__ == "__main__":
    asyncio.run(main())
