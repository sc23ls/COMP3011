import numpy as np
from app.analytics.rates import get_cross_rates


def calculate_volatility(db, base, target):

    prices = get_cross_rates(db, base, target)

    if len(prices) < 2:
        return None

    returns = np.diff(prices) / prices[:-1]

    return float(np.std(returns))