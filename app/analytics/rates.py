from app.models.exchange_rate import ExchangeRate


def get_cross_rates(db, base, target):

    base = base.upper()
    target = target.upper()

    # direct case (EUR base)
    if base == "EUR":
        rates = (
            db.query(ExchangeRate.date, ExchangeRate.rate)
            .filter(
                ExchangeRate.base_currency == "EUR",
                ExchangeRate.target_currency == target
            )
            .order_by(ExchangeRate.date)
            .all()
        )
        return [r.rate for r in rates]

    if target == "EUR":
        rates = (
            db.query(ExchangeRate.date, ExchangeRate.rate)
            .filter(
                ExchangeRate.base_currency == "EUR",
                ExchangeRate.target_currency == base
            )
            .order_by(ExchangeRate.date)
            .all()
        )
        return [1 / r.rate for r in rates]

    # cross-rate case
    base_rates = (
        db.query(ExchangeRate.date, ExchangeRate.rate)
        .filter(
            ExchangeRate.base_currency == "EUR",
            ExchangeRate.target_currency == base
        )
        .order_by(ExchangeRate.date)
        .all()
    )

    target_rates = (
        db.query(ExchangeRate.date, ExchangeRate.rate)
        .filter(
            ExchangeRate.base_currency == "EUR",
            ExchangeRate.target_currency == target
        )
        .order_by(ExchangeRate.date)
        .all()
    )

    return [
        target_rates[i].rate / base_rates[i].rate
        for i in range(min(len(base_rates), len(target_rates)))
    ]