import numpy as np
from app.analytics.rates import get_cross_rates


def detect_trend(db, base, target):

    series = get_cross_rates(db, base, target)

    prices = [r[1] for r in series]

    if len(prices) < 30:
        return "insufficient data"

    prices = list(reversed(prices[-30:]))

    # print("FIRST PRICE:", prices[0])
    # print("LAST PRICE:", prices[-1])
    # print("CHANGE:", prices[-1] - prices[0])

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