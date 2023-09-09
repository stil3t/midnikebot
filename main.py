import asyncio
from robot.strategies import MACD
from robot.client import request_iterator, invest_client
from tinkoff.invest import (
    AsyncClient,
    CandleInstrument,
    MarketDataRequest,
    SubscribeCandlesRequest,
    SubscriptionAction,
    SubscriptionInterval,
)
from robot.load_settings import settings
from robot.get_data import ticker_table
import robot.utils as utils


async def main():
    await invest_client.ainit()
    strategy = MACD.MovingAverageStrategy('SBER')
    await strategy.setup()
    while True:
        await strategy.trade()


if __name__ == "__main__":
    asyncio.run(main())
