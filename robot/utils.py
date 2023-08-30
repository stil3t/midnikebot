# thx to qwertyo1 on github
from tinkoff.invest import Quotation
import math


def qtof(q):
    return float(q.units + q.nano * 10**-9)


def ftoq(f: float):
    return Quotation(*math.modf(f))


def ema(data, window):
    # numpy_ewma_vectorized_v2
    # thx to Divakar on stackoverflow
    alpha = 2 /(window + 1.)
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
