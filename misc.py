import math
import numpy as np
from tinkoff.invest import Quotation


# thx to qwertyo1
@np.vectorize
def quotation_to_float(quotation) -> float:
    return float(quotation.units + quotation.nano * 10**-9)


@np.vectorize
def float_to_quotation(f: float) -> Quotation:
    return Quotation(*math.modf(f))
