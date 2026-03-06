import numpy as np
from app.analytics.rates import get_cross_rates


def detect_trend(db, base, target):

    prices = get_cross_rates(db, base, target)

    if len(prices) < 60:
        return "insufficient data"

    prices = prices[-60:]

    recent_avg = np.mean(prices[-30:])
    older_avg = np.mean(prices[:30])

    if recent_avg > older_avg:
        return "uptrend"
    elif recent_avg < older_avg:
        return "downtrend"
    else:
        return "stable"