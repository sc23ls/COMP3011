from fastapi import APIRouter
from app.database import SessionLocal
from app.analytics.volatility import calculate_volatility
from app.analytics.trend import detect_trend
from app.analytics.regime import detect_regime
from app.models.exchange_rate import ExchangeRate
from app.analytics.rates import get_cross_rates


router = APIRouter()


@router.get("/volatility")
def get_volatility(base: str, target: str):

    db = SessionLocal()

    vol = calculate_volatility(db, base, target)

    db.close()

    if vol is None:
        return {"error": "Not enough data"}

    return {
        "base": base,
        "target": target,
        "volatility": round(vol, 6)
    }

@router.get("/trend")
def get_trend(base: str, target: str):

    db = SessionLocal()

    trend = detect_trend(db, base, target)

    db.close()

    return {
        "base": base,
        "target": target,
        "trend": trend
    }

@router.get("/regime")
def get_regime(base: str, target: str):

    db = SessionLocal()

    result = detect_regime(db, base, target)

    db.close()

    if result is None:
        return {"error": "Insufficient data"}

    return {
        "base": base,
        "target": target,
        "trend": result["trend"],
        "volatility": round(result["volatility"], 6),
        "regime": result["regime"]
    }

@router.get("/latest")
def latest_rate(base: str, target: str):

    db = SessionLocal()

    rate = (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency == base,
            ExchangeRate.target_currency == target
        )
        .order_by(ExchangeRate.date.desc())
        .first()
    )

    db.close()

    if not rate:
        return {"error": "Rate not found"}

    return {
        "base": base,
        "target": target,
        "date": rate.date,
        "rate": rate.rate
    }

@router.get("/history")
def history(base: str, target: str, days: int = 30):

    db = SessionLocal()

    series = get_cross_rates(db, base, target)

    db.close()

    if not series:
        return {"error": "Currency pair not found"}

    series = series[-days:]

    return {
        "base": base,
        "target": target,
        "rates": [
            {"date": d, "rate": r}
            for d, r in series
        ]
    }


@router.get("/currencies")
def get_currencies():

    db = SessionLocal()

    # find most recent date in dataset
    latest_date = db.query(ExchangeRate.date).order_by(ExchangeRate.date.desc()).first()[0]

    currencies = (
        db.query(ExchangeRate.target_currency)
        .filter(ExchangeRate.date == latest_date)
        .distinct()
        .all()
    )

    db.close()

    currency_list = sorted([c[0] for c in currencies])

    currency_list.insert(0, "EUR")

    return {"currencies": currency_list}
