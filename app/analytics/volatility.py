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
        .all()
    )

    # extract numeric values
    rates = [r[0] for r in rates]

    if len(rates) < 2:
        return None

    volatility = float(np.std(rates))

    return volatility