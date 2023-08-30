import asyncio

import pandas as pd
from tinkoff.invest import AsyncClient

import candles
import order
import strategies.MACD
from load_settings import settings

import matplotlib.pyplot as plt

TOKEN = settings.token
ACCOUNT_ID = settings.account_id

async def main():
    async with AsyncClient(TOKEN) as client:
        cndls = await candles.get_1m_candles('RUAL', client, nmins=60)
        cndls = pd.DataFrame(cndls)
        print(cndls.head())
        # MACD_RUAL = robot.strategies.MACD.MovingAverageStrategy(ticker='SBER',
        #                                                         client=client)
        # MACD_RUAL.setup()


if __name__ == "__main__":
    asyncio.run(main())
