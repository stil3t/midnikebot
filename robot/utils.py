from tinkoff.invest import Quotation
from datetime import timedelta
from dataclasses import asdict
from typing import Union
import math
import numpy as np


def qtof(q: Union[Quotation, dict]) -> float:
    if type(q) is dict:
        return float(q['units'] + q['nano'] * 10**-9)
    elif type(q) is Quotation:
        return float(q.units + q.nano * 10**-9)
    else:
        raise NotImplementedError


def ftoq(f: float) -> Quotation:
    return Quotation(*math.modf(f))


def ema(data, window):
    # numpy_ewma_vectorized_v2
    # thx to Divakar on stackoverflow
    alpha = 2 / (window + 1.)
    alpha_rev = 1 - alpha
    n = data.shape[0]

    pows = alpha_rev**(np.arange(n+1))

    scale_arr = 1 / pows[:-1]
    offset = data[0] * pows[1:]
    pw0 = alpha * alpha_rev**(n-1)

    mult = data * pw0 * scale_arr
    cumsums = mult.cumsum()
    out = offset + cumsums * scale_arr[::-1]
    return out


def ema_new_val(new_val, prev_ema, window):
    alpha = 2 / (window + 1.)
    alpha_rev = 1 - alpha
    return new_val * alpha + prev_ema * alpha_rev


def process_candle(candle):
    try:
        candle = asdict(candle)
        for attr in ['open', 'high', 'low', 'close']:
            candle[attr] = qtof(candle[attr])
        candle['time'] += timedelta(hours=3)  # converting to Moscow time
        return candle
    except Exception:
        return None
