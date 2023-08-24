import numpy as np

O = 10**-3

def moving_average(x, w):
    # thx yatu
    # return np.convolve(x, np.ones(w), 'valid') / w
    return x.rolling(w).mean()


def rsi(x, n=14):
    assert len(x) > n, 'Not enough data'
    x0, x1 = np.diff(x), np.diff(x)
    x0[x0 < 0] = 0
    x1[x1 > 0] = 0
    avg_gain = moving_average(x0, n)
    avg_loss = moving_average(x1, n)
    return 100 - 100 / (1 - avg_gain / avg_loss)
    # return x1

