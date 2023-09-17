import asyncio
from robot.strategies import MACD, RSI
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
    # await invest_client.ainit()
    # strategy = RSI.RelativeStrengthIndicatorStrategy('SBER')
    # await strategy.setup()
    # while True:
    #     await strategy.trade()
    pass


if __name__ == "__main__":
    asyncio.run(main())
