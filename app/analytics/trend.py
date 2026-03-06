import numpy as np
from sqlalchemy.orm import Session
from app.models.exchange_rate import ExchangeRate


def detect_trend(db: Session, base: str, target: str):

    rates = (
        db.query(ExchangeRate.rate)
        .filter(
            ExchangeRate.base_currency == base,
            ExchangeRate.target_currency == target
        )
        .order_by(ExchangeRate.date.desc())
        .limit(60)
        .all()
    )

    # extract values
    rates = [r[0] for r in rates]

    if len(rates) < 60:
        return "insufficient data"

    recent_avg = np.mean(rates[:30])
    older_avg = np.mean(rates[30:60])

    if recent_avg > older_avg:
        return "uptrend"
    elif recent_avg < older_avg:
        return "downtrend"
    else:
        return "stable"