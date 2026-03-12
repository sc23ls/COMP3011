import numpy as np
from app.analytics.rates import get_cross_rates


def detect_trend(db, base, target):

    series = get_cross_rates(db, base, target)

    prices = [rate for _, rate in series if rate is not None and np.isfinite(rate)]

    if len(prices) < 30:
        return "insufficient data"

    # get_cross_rates returns chronological data, so keep oldest->newest order
    prices = prices[-30:]

    start_price = prices[0]
    end_price = prices[-1]

    change = end_price - start_price

    threshold = 0.0005

    if change > threshold:
        return "uptrend"
    elif change < -threshold:
        return "downtrend"
    else:
        return "stable"
