from app.analytics.volatility import calculate_volatility
from app.analytics.trend import detect_trend


def detect_regime(db, base, target):

    vol = calculate_volatility(db, base, target)
    trend = detect_trend(db, base, target)

    if vol is None:
        return None

    if vol > 0.01:
        vol_level = "high volatility"
    else:
        vol_level = "low volatility"

    regime = f"{vol_level} {trend}"

    return {
        "trend": trend,
        "volatility": vol,
        "regime": regime
    }