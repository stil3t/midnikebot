import dask.dataframe as dd
import pandas as pd
from datetime import date, datetime

import asyncio
import os

from tinkoff.invest.grpc.orders_pb2 import OrderExecutionReportStatus

from robot.load_settings import settings
from robot.get_data import ticker_table
from robot.utils import qtof


class DB:

    def __init__(self, name: str):
        self.name = name.lower()
        self.df = None
        self.df_today = None

    def load_today(self):
        filename = f'./{self.name}/{self.name}_{date.today()}.csv'
        if os.path.exists(filename):
            self.df_today = pd.read_csv(filename)
        else:
            self.create()

    def load(self):
        if not (os.listdir(f'./{self.name}')):
            self.create()
        self.df = dd.read_csv(f'./{self.name}/{self.name}_*.csv')

    def read_day(self, day):
        return self.df[self.df['date'] == day]

    def create(self, columns=None):
        name_to_cols = {'orders': ['date', 'time', 'ticker', 'action', 'lot_quantity', 'lot_price', 'price']}
        if columns is None:
            columns = name_to_cols[self.name]

        self.df_today = pd.DataFrame(columns=columns, index=[])
        self.df_today.to_csv(f'./{self.name}/{self.name}_{date.today()}.csv')

    async def new_entry(self, order, client):
        while True:
            state = await client.orders.get_order_state(account_id=settings.account_id, order_id=order.order_id)

            if state.execution_report_status == OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_REJECTED:
                print('Order rejected')
                break

            if state.execution_report_status == OrderExecutionReportStatus.EXECUTION_REPORT_STATUS_PARTIALLYFILL:
                await asyncio.sleep(5)
                continue

            row = {'date': state.order_date.date(), 'time': state.order_date.time(),
                   'ticker': ticker_table.get_by_figi(state.figi), 'action': state.dircetion.split('_')[-1],
                   'lot_quantity': state.lots_executed, 'lot_price': qtof(state.average_position_price),
                   'price': qtof(state.total_order_amount)}
            self.df_today = pd.concat([self.df_today, pd.DataFrame(row)])


db = DB('orders')
db.load()
db.load_today()
