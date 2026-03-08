from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.exchange_rate import ExchangeRate

router = APIRouter()


@router.get("/convert")
def convert_currency(base: str, target: str, amount: float, db: Session = Depends(get_db)):

    base = base.upper()
    target = target.upper()

    # if currencies are the same
    if base == target:
        return {
            "base": base,
            "target": target,
            "rate": 1,
            "amount": amount,
            "converted": amount
        }

    # get latest EUR -> base rate
    base_rate = (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency == "EUR",
            ExchangeRate.target_currency == base
        )
        .order_by(ExchangeRate.date.desc())
        .first()
    )

    # get latest EUR -> target rate
    target_rate = (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency == "EUR",
            ExchangeRate.target_currency == target
        )
        .order_by(ExchangeRate.date.desc())
        .first()
    )

    # handle cases where currency isn't found
    if base != "EUR" and not base_rate:
        return {"error": f"Currency {base} not found"}

    if target != "EUR" and not target_rate:
        return {"error": f"Currency {target} not found"}

    # calculate conversion rate
    if base == "EUR":
        rate = target_rate.rate

    elif target == "EUR":
        rate = 1 / base_rate.rate

    else:
        rate = target_rate.rate / base_rate.rate

    converted_amount = amount * rate

    return {
        "base": base,
        "target": target,
        "rate": round(rate, 6),
        "amount": amount,
        "converted": round(converted_amount, 2)
    }