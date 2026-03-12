from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.analytics.rates import get_cross_rates
from app.analytics.regime import detect_regime
from app.analytics.trend import detect_trend
from app.analytics.volatility import calculate_volatility
from app.database import get_db
from app.models.exchange_rate import ExchangeRate


router = APIRouter()


def normalize_currency(code: str, field_name: str) -> str:
    currency = str(code).strip().upper()
    if len(currency) != 3 or not currency.isalpha():
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} must be a valid 3-letter currency code",
        )
    return currency


def ensure_distinct_pair(base: str, target: str) -> None:
    if base == target:
        raise HTTPException(
            status_code=422,
            detail="Base and target are the same currency. Conversion rate is always 1.",
        )


@router.get("/volatility")
def get_volatility(base: str, target: str, db: Session = Depends(get_db)):
    base = normalize_currency(base, "base")
    target = normalize_currency(target, "target")
    ensure_distinct_pair(base, target)

    try:
        vol = calculate_volatility(db, base, target)
        if vol is None:
            raise HTTPException(status_code=422, detail="Not enough data")

        return {
            "base": base,
            "target": target,
            "volatility": round(vol, 6),
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error while calculating volatility",
        ) from exc


@router.get("/trend")
def get_trend(base: str, target: str, db: Session = Depends(get_db)):
    base = normalize_currency(base, "base")
    target = normalize_currency(target, "target")
    ensure_distinct_pair(base, target)

    try:
        trend = detect_trend(db, base, target)
        if trend == "insufficient data":
            raise HTTPException(status_code=422, detail="Not enough data")

        return {
            "base": base,
            "target": target,
            "trend": trend,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error while detecting trend",
        ) from exc


@router.get("/regime")
def get_regime(base: str, target: str, db: Session = Depends(get_db)):
    base = normalize_currency(base, "base")
    target = normalize_currency(target, "target")
    ensure_distinct_pair(base, target)

    try:
        result = detect_regime(db, base, target)
        if result is None:
            raise HTTPException(status_code=422, detail="Insufficient data")

        return {
            "base": base,
            "target": target,
            "trend": result["trend"],
            "volatility": round(result["volatility"], 6),
            "regime": result["regime"],
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error while classifying market regime",
        ) from exc


@router.get("/latest")
def latest_rate(base: str, target: str, db: Session = Depends(get_db)):
    base = normalize_currency(base, "base")
    target = normalize_currency(target, "target")
    ensure_distinct_pair(base, target)

    try:
        series = get_cross_rates(db, base, target)
        if not series:
            raise HTTPException(status_code=404, detail="Rate not found")

        latest_date, latest_rate_value = series[-1]
        return {
            "base": base,
            "target": target,
            "date": latest_date,
            "rate": latest_rate_value,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching latest rate",
        ) from exc


@router.get("/history")
def history(
    base: str,
    target: str,
    days: int = 30,
    db: Session = Depends(get_db),
):
    base = normalize_currency(base, "base")
    target = normalize_currency(target, "target")
    ensure_distinct_pair(base, target)
    if days <= 0:
        raise HTTPException(status_code=422, detail="days must be greater than 0")

    try:
        series = get_cross_rates(db, base, target)
        if not series:
            raise HTTPException(status_code=404, detail="Currency pair not found")

        series = series[-days:]
        return {
            "base": base,
            "target": target,
            "rates": [{"date": d, "rate": r} for d, r in series],
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching history",
        ) from exc


@router.get("/currencies")
def get_currencies(db: Session = Depends(get_db)):
    try:
        latest_date_record = (
            db.query(ExchangeRate.date).order_by(ExchangeRate.date.desc()).first()
        )
        if not latest_date_record:
            raise HTTPException(status_code=404, detail="No rates available")

        latest_date = latest_date_record[0]
        currencies = (
            db.query(ExchangeRate.target_currency)
            .filter(ExchangeRate.date == latest_date)
            .distinct()
            .all()
        )

        currency_list = sorted({c[0] for c in currencies if c[0]})
        if "EUR" not in currency_list:
            currency_list.insert(0, "EUR")

        return {"currencies": currency_list}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error while fetching currencies",
        ) from exc
