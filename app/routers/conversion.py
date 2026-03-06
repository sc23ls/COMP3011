from fastapi import APIRouter
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate

router = APIRouter()


@router.get("/convert")
def convert_currency(base: str, target: str, amount: float):

    db: Session = SessionLocal()

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
        return {"error": "Exchange rate not found"}

    converted_amount = amount * rate.rate

    return {
        "base": base,
        "target": target,
        "rate": rate.rate,
        "amount": amount,
        "converted": round(converted_amount, 2)
    }