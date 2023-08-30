import pandas as pd
import os

from tinkoff.invest import Client
from tinkoff.invest.services import InstrumentsService
from tinkoff.invest.utils import quotation_to_decimal

from load_settings import settings

TOKEN = settings.token


def get_data():
    global TOKEN
    with Client(TOKEN) as client:
        instruments: InstrumentsService = client.instruments
        df = []
        for method in ["shares", "bonds", "etfs", "currencies", "futures"]:
            for item in getattr(instruments, method)().instruments:
                df.append(
                    {
                        "name": item.name,
                        "ticker": item.ticker,
                        "figi": item.figi,
                        "type": method,
                        "min_price_increment": quotation_to_decimal(item.min_price_increment),
                        "lot": item.lot,
                        "klong": quotation_to_decimal(item.klong),
                        "kshort": quotation_to_decimal(item.kshort)
                    }
                )

    return pd.DataFrame(df)


class TickerTable:

    def __init__(self, *, update=False):
        if os.path.exists('ticker_table.csv') and not update:
            self.df = pd.read_csv('ticker_table.csv', index_col=0)
        else:
            self.update()

    def __getitem__(self, ticker: str) -> pd.Series:
        return self.df.loc[ticker]

    def update(self) -> None:
        self.df = get_data()
        self.df = self.df.set_index('ticker')
        self.df.to_csv('ticker_table.csv')


ticker_table = TickerTable()

