import numpy as np
from sqlalchemy.orm import Session
from app.models.exchange_rate import ExchangeRate


def calculate_volatility(db: Session, base: str, target: str):

    rates = (
        db.query(ExchangeRate.rate)
        .filter(
            ExchangeRate.base_currency == base,
            ExchangeRate.target_currency == target
        )
        .order_by(ExchangeRate.date)
        .all()
    )

    prices = [r[0] for r in rates]

    if len(prices) < 2:
        return None

    # calculate daily returns
    returns = np.diff(prices) / prices[:-1]

    volatility = float(np.std(returns))

    return volatility