import pandas as pd

from load_settings import settings
from get_figi import ticker_table

import asyncio
import candles

from tinkoff.invest import AsyncClient

TOKEN = settings.token
ACCOUNT_ID = settings.account_id
TICKER = 'FLOT'


async def main():
    async with AsyncClient(TOKEN) as client:
        try:
            cndls = await candles.get_1m_candles(TICKER, client)
            df = pd.DataFrame(cndls)
            df.set_index('time', inplace=True)
            print(df.tail(3))
            while True:
                lst = await candles.get_1m_candles(TICKER, client, nmins=1)
                print(lst)
                await asyncio.sleep(5)
        except KeyboardInterrupt:
            pass
        # finally:
        #     await client.cancel_all_orders(account_id=ACCOUNT_ID)


if __name__ == "__main__":
    asyncio.run(main())
