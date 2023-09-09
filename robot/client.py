from typing import Optional
from uuid import uuid4
import asyncio
from datetime import timedelta

from robot.load_settings import settings
from robot.get_data import ticker_table
from robot.utils import qtof, ftoq, process_candle

from tinkoff.invest.grpc.orders_pb2 import (ORDER_DIRECTION_SELL, ORDER_DIRECTION_BUY, ORDER_TYPE_MARKET,
                                            ORDER_TYPE_LIMIT, )
from tinkoff.invest.async_services import AsyncServices
from tinkoff.invest import (AsyncClient, PostOrderResponse, GetLastPricesResponse, OrderState, GetTradingStatusResponse,
                            InstrumentResponse, )
from tinkoff.invest.utils import now

from tinkoff.invest import (CandleInstrument, MarketDataRequest, SubscribeCandlesRequest, SubscriptionAction,
                            SubscriptionInterval, CandleInterval)


async def request_iterator(ticker):
    yield MarketDataRequest(subscribe_candles_request=SubscribeCandlesRequest(
        subscription_action=SubscriptionAction.SUBSCRIPTION_ACTION_SUBSCRIBE, instruments=[
            CandleInstrument(figi=ticker_table[ticker].figi,
                             interval=SubscriptionInterval.SUBSCRIPTION_INTERVAL_ONE_MINUTE, )], ))
    while True:
        await asyncio.sleep(3)


class Client:
    def __init__(self, token: str):
        self.token = token
        self.client: Optional[AsyncServices] = None

    async def ainit(self):
        self.client = await AsyncClient(token=self.token).__aenter__()

    async def get_position(self, ticker):
        positions = (await self.client.operations.get_portfolio(account_id=settings.account_id)).positions
        for pos in positions:
            if pos.figi == ticker_table[ticker].figi:
                return pos
        else:
            return None

    async def get_rubs(self):
        positions = (await self.client.operations.get_portfolio(account_id=settings.account_id)).positions
        for pos in positions:
            if pos.figi == 'RUB000UTSTOM':
                return qtof(pos.quantity)

    async def get_orders(self, **kwargs):
        return await self.client.orders.get_orders(**kwargs)

    async def get_accounts(self):
        return await self.client.users.get_accounts()

    async def buy(self, ticker, quantity) -> PostOrderResponse:
        # market buy
        ordr = await self.client.orders.post_order(order_id=str(uuid4()), figi=ticker_table[ticker].figi,
                                                   direction=ORDER_DIRECTION_BUY, quantity=quantity,
                                                   order_type=ORDER_TYPE_MARKET, account_id=settings.account_id)
        await asyncio.sleep(10)
        print(f'{now()}: bought {ticker}, {quantity}')
        return ordr

    async def sell(self, ticker, quantity) -> PostOrderResponse:
        # market sell
        ordr = await self.client.orders.post_order(order_id=str(uuid4()), figi=ticker_table[ticker].figi,
                                                   direction=ORDER_DIRECTION_SELL, quantity=quantity,
                                                   order_type=ORDER_TYPE_MARKET, account_id=settings.account_id)
        await asyncio.sleep(10)
        print(f'{now()}: sold {ticker}, {quantity}')
        return ordr

    async def limited_buy(self, ticker, price, quantity) -> PostOrderResponse:
        # market buy
        ordr = await self.client.orders.post_order(order_id=str(uuid4()), figi=ticker_table[ticker].figi,
                                                   direction=ORDER_DIRECTION_BUY, quantity=quantity, price=price,
                                                   order_type=ORDER_TYPE_LIMIT, account_id=settings.account_id)
        await asyncio.sleep(10)
        return ordr

    async def limited_sell(self, ticker, price, quantity) -> PostOrderResponse:
        # market sell
        ordr = await self.client.orders.post_order(order_id=str(uuid4()), figi=ticker_table[ticker].figi,
                                                   direction=ORDER_DIRECTION_SELL, quantity=quantity, price=price,
                                                   order_type=ORDER_TYPE_LIMIT, account_id=settings.account_id)
        await asyncio.sleep(10)
        return ordr

    async def get_1m_candles(self, ticker, nmins=60):
        data = []
        async for candle in self.client.get_all_candles(figi=ticker_table[ticker].figi,
                                                        from_=now() - timedelta(minutes=nmins),
                                                        interval=CandleInterval.CANDLE_INTERVAL_1_MIN):
            data.append(process_candle(candle))
            # data.append(candle)

        await asyncio.sleep(2)
        return data


invest_client = Client(token=settings.token)
