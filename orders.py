import asyncio
from uuid import uuid4

from load_settings import settings
from get_figi import ticker_table

TOKEN = settings.token
ACCOUNT_ID = settings.account_id

from tinkoff.invest.grpc.orders_pb2 import (

    ORDER_DIRECTION_SELL,
    ORDER_DIRECTION_BUY,

    ORDER_TYPE_MARKET,
    ORDER_TYPE_LIMIT,

)


async def buy(ticker, quantity, client):

    # market buy
    ordr = client.orders.post_order(
        order_id=str(uuid4()),
        figi=ticker_table[ticker],
        direction=ORDER_DIRECTION_BUY,
        quantity=quantity,
        order_type=ORDER_TYPE_MARKET,
        account_id=ACCOUNT_ID
    )
    return ordr


async def sell(ticker, quantity, client):
    # market sell
    ordr = client.orders.post_order(
        order_id=str(uuid4()),
        figi=ticker_table[ticker],
        direction=ORDER_DIRECTION_SELL,
        quantity=quantity,
        order_type=ORDER_TYPE_MARKET,
        account_id=ACCOUNT_ID
    )
    return ordr


async def lbuy(ticker, price, quantity, client):

    # market buy
    ordr = client.orders.post_order(
        order_id=str(uuid4()),
        figi=ticker_table[ticker],
        direction=ORDER_DIRECTION_BUY,
        quantity=quantity,
        price=price,
        order_type=ORDER_TYPE_LIMIT,
        account_id=ACCOUNT_ID
    )
    return ordr


async def lsell(ticker, price, quantity, client):
    # market sell
    ordr = client.orders.post_order(
        order_id=str(uuid4()),
        figi=ticker_table[ticker],
        direction=ORDER_DIRECTION_SELL,
        quantity=quantity,
        price=price,
        order_type=ORDER_TYPE_LIMIT,
        account_id=ACCOUNT_ID
    )
    return ordr
