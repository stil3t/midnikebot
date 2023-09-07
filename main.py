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
    await strategy.trade()

    # it = request_iterator('SBER')
    # it = invest_client.client.market_data_stream.market_data_stream(it)
    # print(await anext(it))

    # async for candle in invest_client.client.get_all_candles(figi="BBG000B9XRY4", from_=now() - timedelta(days=3),
    #         interval=CandleInterval.CANDLE_INTERVAL_1_MIN, ):
    #     print(candle)



if __name__ == "__main__":
    asyncio.run(main())
