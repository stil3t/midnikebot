import numpy as np


def moving_average(x, w):
    # thx yatu
    return np.convolve(x, np.ones(w), 'valid') / w


def rsi(x, n=14):
    assert len(x) > n, 'Not enough data'
    x0, x1 = np.diff(x), np.diff(x)
    x0[x0 < 0] = 0
    x1[x1 > 0] = 0
    avg_gain = moving_average(x0, n)
    avg_loss = moving_average(x1, n)
    return 100 - 100 / (1 - avg_gain / avg_loss)
    # return x1

print(rsi(np.array(
    [140.06, 144.28, 147.64, 150.6, 151.92, 154.79, 152.61, 150.26, 150.47, 146.68, 145.14, 148.1, 148.82, 148.91,
     147.21, 142.84, 145.48])))
