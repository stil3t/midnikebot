import asyncio
import numpy as np
import pandas as pd
from datetime import timedelta
from dataclasses import asdict

from get_figi import ticker_table
from misc import quotation_to_float, float_to_quotation

from tinkoff.invest.utils import now

from tinkoff.invest import (CandleInstrument, MarketDataRequest, SubscribeCandlesRequest, SubscriptionAction,
                            SubscriptionInterval, CandleInterval)


async def get_1m_candles(ticker, client, nmins=60):
    data = []
    async for candle in client.get_all_candles(figi=ticker_table[ticker].figi, from_=now() - timedelta(minutes=nmins),
                                               interval=CandleInterval.CANDLE_INTERVAL_1_MIN, ):
        data.append(await process_candle(candle))

    return data


async def process_candle(candle):
    try:
        candle = asdict(candle)
        for attr in ['open', 'high', 'low', 'close']:
            candle[attr] = candle[attr]['units'] + candle[attr]['nano'] * 10 ** -9
        candle['time'] += timedelta(hours=3)  # converting to Moscow time
        return candle
    except Exception:
        return None


async def request_iterator(ticker):
    yield MarketDataRequest(subscribe_candles_request=SubscribeCandlesRequest(
        subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE, instruments=[
            CandleInstrument(figi=ticker_table[ticker].figi,
                             interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE, )], ))
    while True:
        await asyncio.sleep(5)
