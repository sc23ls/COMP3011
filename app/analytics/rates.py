from app.models.exchange_rate import ExchangeRate


def get_cross_rates(db, base, target):

    base = str(base).strip().upper()
    target = str(target).strip().upper()

    if not base or not target:
        return []

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
        return [(r.date, 1 / r.rate) for r in rates if r.rate not in (None, 0)]

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

    base_by_date = {
        rate.date: rate.rate
        for rate in base_rates
        if rate.rate not in (None, 0)
    }
    target_by_date = {
        rate.date: rate.rate
        for rate in target_rates
        if rate.rate is not None
    }

    shared_dates = sorted(set(base_by_date).intersection(target_by_date))

    return [
        (rate_date, target_by_date[rate_date] / base_by_date[rate_date])
        for rate_date in shared_dates
    ]
