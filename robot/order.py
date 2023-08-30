import asyncio
from uuid import uuid4

from load_settings import settings
from get_data import ticker_table

from tinkoff.invest.grpc.orders_pb2 import (

    ORDER_DIRECTION_SELL, ORDER_DIRECTION_BUY,

    ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT,

)


async def get_pos(ticker, client):
    positions = (await client.operations.get_portfolio(account_id=settings.account_id)).positions
    for pos in positions:
        if pos.figi == ticker_table[ticker].figi:
            return pos

async def get_balance(client):
    positions = (await client.operations.get_portfolio(account_id=settings.account_id)).positions
    for pos in positions:
        if pos.figi == RUB000UTSTOM:
            return qtof(pos.quantity)

async def buy(ticker, quantity, client):
    # market buy
    await client.orders.post_order(order_id=str(uuid4()), figi=ticker_table[ticker].figi, direction=ORDER_DIRECTION_BUY,
                                   quantity=quantity, order_type=ORDER_TYPE_MARKET, account_id=settings.account_id)
    await asyncio.sleep(10)


async def sell(ticker, quantity, client):
    # market sell
    await client.orders.post_order(order_id=str(uuid4()), figi=ticker_table[ticker].figi,
                                   direction=ORDER_DIRECTION_SELL, quantity=quantity, order_type=ORDER_TYPE_MARKET,
                                   account_id=settings.account_id)
    await asyncio.sleep(10)


async def lbuy(ticker, price, quantity, client):
    # market buy
    await client.orders.post_order(order_id=str(uuid4()), figi=ticker_table[ticker].figi, direction=ORDER_DIRECTION_BUY,
                                   quantity=quantity, price=price, order_type=ORDER_TYPE_LIMIT,
                                   account_id=settings.account_id)
    await asyncio.sleep(10)


async def lsell(ticker, price, quantity, client):
    # market sell
    await client.orders.post_order(order_id=str(uuid4()), figi=ticker_table[ticker].figi,
                                   direction=ORDER_DIRECTION_SELL, quantity=quantity, price=price,
                                   order_type=ORDER_TYPE_LIMIT, account_id=settings.account_id)
    await asyncio.sleep(10)
