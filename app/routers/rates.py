from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.exchange_rate import ExchangeRate
from app.schemas.rate import RateCreate, RateUpdate

from app.services.auth import get_current_user
from fastapi import Depends

router = APIRouter(prefix="/rates", tags=["Rates"])


@router.get("/")
def get_rates():

    db: Session = SessionLocal()

    rates = db.query(ExchangeRate).limit(100).all()

    db.close()

    return rates


@router.post("/")
def create_rate(rate: RateCreate, user=Depends(get_current_user)):

    db: Session = SessionLocal()

    new_rate = ExchangeRate(
        base_currency=rate.base_currency.upper(),
        target_currency=rate.target_currency.upper(),
        rate=rate.rate,
        date=rate.date
    )

    db.add(new_rate)
    db.commit()

    db.refresh(new_rate)

    db.close()

    return new_rate


@router.put("/{rate_id}")
def update_rate(rate_id: int, update: RateUpdate, user=Depends(get_current_user)):

    db: Session = SessionLocal()

    rate = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()

    if not rate:
        db.close()
        raise HTTPException(status_code=404, detail="Rate not found")

    rate.rate = update.rate

    db.commit()

    db.refresh(rate)

    db.close()

    return rate


@router.delete("/{rate_id}")
def delete_rate(rate_id: int, user=Depends(get_current_user)):

    db: Session = SessionLocal()

    rate = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()

    if not rate:
        db.close()
        raise HTTPException(status_code=404, detail="Rate not found")

    db.delete(rate)
    db.commit()

    db.close()

    return {"message": "Rate deleted"}