import numpy as np
from app.analytics.rates import get_cross_rates


def calculate_volatility(db, base, target):

    series = get_cross_rates(db, base, target)

    prices = [rate for _, rate in series if rate is not None and rate > 0]

    if len(prices) < 2:
        return None

    with np.errstate(divide="ignore", invalid="ignore"):
        returns = np.diff(prices) / prices[:-1]

    returns = returns[np.isfinite(returns)]
    if returns.size == 0:
        return None

    volatility = float(np.std(returns))
    if not np.isfinite(volatility):
        return None

    return volatility
