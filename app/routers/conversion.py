from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

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


@router.get("/convert")
def convert_currency(
    base: str,
    target: str,
    amount: float,
    db: Session = Depends(get_db),
):
    base = normalize_currency(base, "base")
    target = normalize_currency(target, "target")

    if amount <= 0:
        raise HTTPException(status_code=422, detail="amount must be greater than 0")

    if base == target:
        return {
            "base": base,
            "target": target,
            "rate": 1,
            "amount": amount,
            "converted": amount,
        }

    try:
        base_rate = (
            db.query(ExchangeRate)
            .filter(
                ExchangeRate.base_currency == "EUR",
                ExchangeRate.target_currency == base,
            )
            .order_by(ExchangeRate.date.desc())
            .first()
        )

        target_rate = (
            db.query(ExchangeRate)
            .filter(
                ExchangeRate.base_currency == "EUR",
                ExchangeRate.target_currency == target,
            )
            .order_by(ExchangeRate.date.desc())
            .first()
        )

        if base != "EUR" and not base_rate:
            raise HTTPException(status_code=404, detail=f"Currency {base} not found")

        if target != "EUR" and not target_rate:
            raise HTTPException(status_code=404, detail=f"Currency {target} not found")

        if base == "EUR":
            if target_rate.rate in (None, 0):
                raise HTTPException(status_code=422, detail=f"Invalid rate for {target}")
            rate = target_rate.rate
        elif target == "EUR":
            if base_rate.rate in (None, 0):
                raise HTTPException(status_code=422, detail=f"Invalid rate for {base}")
            rate = 1 / base_rate.rate
        else:
            if base_rate.rate in (None, 0):
                raise HTTPException(status_code=422, detail=f"Invalid rate for {base}")
            if target_rate.rate in (None, 0):
                raise HTTPException(status_code=422, detail=f"Invalid rate for {target}")
            rate = target_rate.rate / base_rate.rate

        converted_amount = amount * rate

        return {
            "base": base,
            "target": target,
            "rate": round(rate, 6),
            "amount": amount,
            "converted": round(converted_amount, 2),
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=500,
            detail="Database error while converting currency",
        ) from exc
