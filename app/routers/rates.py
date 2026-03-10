from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exchange_rate import ExchangeRate
from app.schemas.rate import RateCreate, RateUpdate
from app.services.auth import get_current_user

router = APIRouter(prefix="/rates", tags=["Rates"])


def normalize_currency(code: str, field_name: str) -> str:
    currency = str(code).strip().upper()
    if len(currency) != 3 or not currency.isalpha():
        raise HTTPException(
            status_code=422,
            detail=f"{field_name} must be a valid 3-letter currency code",
        )
    return currency


@router.get("/")
def get_rates(db: Session = Depends(get_db)):
    try:
        return db.query(ExchangeRate).limit(100).all()
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while fetching rates") from exc


@router.post("/")
def create_rate(
    rate: RateCreate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    base_currency = normalize_currency(rate.base_currency, "base_currency")
    target_currency = normalize_currency(rate.target_currency, "target_currency")
    if rate.rate <= 0:
        raise HTTPException(status_code=422, detail="rate must be greater than 0")

    new_rate = ExchangeRate(
        base_currency=base_currency,
        target_currency=target_currency,
        rate=rate.rate,
        date=rate.date,
    )

    try:
        db.add(new_rate)
        db.commit()
        db.refresh(new_rate)
        return new_rate
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while creating rate") from exc


@router.put("/{rate_id}")
def update_rate(
    rate_id: int,
    update: RateUpdate,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if update.rate <= 0:
        raise HTTPException(status_code=422, detail="rate must be greater than 0")

    try:
        rate = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
        if not rate:
            raise HTTPException(status_code=404, detail="Rate not found")

        rate.rate = update.rate
        db.commit()
        db.refresh(rate)
        return rate
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while updating rate") from exc


@router.delete("/{rate_id}")
def delete_rate(
    rate_id: int,
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        rate = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
        if not rate:
            raise HTTPException(status_code=404, detail="Rate not found")

        db.delete(rate)
        db.commit()
        return {"message": "Rate deleted"}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while deleting rate") from exc
