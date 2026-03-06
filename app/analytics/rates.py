from app.models.exchange_rate import ExchangeRate


def get_cross_rates(db, base, target):

    base = base.upper()
    target = target.upper()

    if base == target:
        return []

    # EUR → target
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
        return [(r.date, r.rate) for r in rates]

    # base → EUR
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
        return [(r.date, 1 / r.rate) for r in rates]

    # cross-rate
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

    n = min(len(base_rates), len(target_rates))

    return [
        (
            base_rates[i].date,
            target_rates[i].rate / base_rates[i].rate
        )
        for i in range(n)
    ]