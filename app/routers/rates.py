from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import asc, desc, func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Query as SAQuery
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.exchange_rate import ExchangeRate
from app.schemas.rate import (
    RateBulkCreate,
    RateBulkDelete,
    RateCreate,
    RatePatch,
    RateUpdate,
)
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


def ensure_positive_rate(rate_value: float) -> None:
    if rate_value <= 0:
        raise HTTPException(status_code=422, detail="rate must be greater than 0")


def require_admin(user: str = Depends(get_current_user)) -> str:
    if user.lower() != "admin":
        raise HTTPException(status_code=403, detail="Admin privileges are required")
    return user


def apply_rate_filters(
    query: SAQuery,
    base_currency: str | None,
    target_currency: str | None,
    start_date: date | None,
    end_date: date | None,
    min_rate: float | None,
    max_rate: float | None,
) -> SAQuery:
    if base_currency:
        query = query.filter(
            ExchangeRate.base_currency == normalize_currency(base_currency, "base_currency")
        )
    if target_currency:
        query = query.filter(
            ExchangeRate.target_currency == normalize_currency(target_currency, "target_currency")
        )
    if start_date:
        query = query.filter(ExchangeRate.date >= start_date)
    if end_date:
        query = query.filter(ExchangeRate.date <= end_date)
    if min_rate is not None:
        query = query.filter(ExchangeRate.rate >= min_rate)
    if max_rate is not None:
        query = query.filter(ExchangeRate.rate <= max_rate)
    return query


@router.get("/")
def get_rates(
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    try:
        return (
            db.query(ExchangeRate)
            .order_by(ExchangeRate.date.desc(), ExchangeRate.id.desc())
            .limit(limit)
            .all()
        )
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while fetching rates") from exc


@router.get("/search")
def search_rates(
    base_currency: str | None = None,
    target_currency: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    min_rate: float | None = Query(default=None, gt=0),
    max_rate: float | None = Query(default=None, gt=0),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    sort_by: str = Query(default="date"),
    sort_order: str = Query(default="desc"),
    db: Session = Depends(get_db),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="start_date cannot be after end_date")
    if min_rate is not None and max_rate is not None and min_rate > max_rate:
        raise HTTPException(status_code=422, detail="min_rate cannot be greater than max_rate")

    sort_fields = {
        "id": ExchangeRate.id,
        "date": ExchangeRate.date,
        "rate": ExchangeRate.rate,
    }
    if sort_by not in sort_fields:
        raise HTTPException(status_code=422, detail="sort_by must be one of: id, date, rate")
    if sort_order not in {"asc", "desc"}:
        raise HTTPException(status_code=422, detail="sort_order must be 'asc' or 'desc'")

    try:
        query = apply_rate_filters(
            db.query(ExchangeRate),
            base_currency,
            target_currency,
            start_date,
            end_date,
            min_rate,
            max_rate,
        )

        total = query.count()
        sort_column = sort_fields[sort_by]
        query = query.order_by(desc(sort_column) if sort_order == "desc" else asc(sort_column))
        items = query.offset(skip).limit(limit).all()

        return {
            "total": total,
            "count": len(items),
            "skip": skip,
            "limit": limit,
            "items": items,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while searching rates") from exc


@router.get("/stats/summary")
def get_rate_summary(
    base_currency: str | None = None,
    target_currency: str | None = None,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        query = apply_rate_filters(
            db.query(ExchangeRate),
            base_currency,
            target_currency,
            start_date=None,
            end_date=None,
            min_rate=None,
            max_rate=None,
        )

        summary = query.with_entities(
            func.count(ExchangeRate.id),
            func.min(ExchangeRate.rate),
            func.max(ExchangeRate.rate),
            func.avg(ExchangeRate.rate),
            func.max(ExchangeRate.date),
        ).first()

        total, min_value, max_value, avg_value, latest_date = summary
        return {
            "total_rates": total,
            "min_rate": float(min_value) if min_value is not None else None,
            "max_rate": float(max_value) if max_value is not None else None,
            "average_rate": round(float(avg_value), 6) if avg_value is not None else None,
            "latest_date": latest_date,
            "requested_by": user,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while building summary") from exc


@router.get("/{rate_id}")
def get_rate_by_id(rate_id: int, db: Session = Depends(get_db)):
    try:
        rate = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
        if not rate:
            raise HTTPException(status_code=404, detail="Rate not found")
        return rate
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while fetching rate") from exc


@router.post("/")
def create_rate(
    rate: RateCreate,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    base_currency = normalize_currency(rate.base_currency, "base_currency")
    target_currency = normalize_currency(rate.target_currency, "target_currency")
    ensure_positive_rate(rate.rate)

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


@router.post("/bulk")
def create_rates_bulk(
    payload: RateBulkCreate,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_rates: list[ExchangeRate] = []

    try:
        for incoming in payload.rates:
            base_currency = normalize_currency(incoming.base_currency, "base_currency")
            target_currency = normalize_currency(incoming.target_currency, "target_currency")
            ensure_positive_rate(incoming.rate)

            new_rate = ExchangeRate(
                base_currency=base_currency,
                target_currency=target_currency,
                rate=incoming.rate,
                date=incoming.date,
            )
            db.add(new_rate)
            new_rates.append(new_rate)

        db.commit()
        for new_rate in new_rates:
            db.refresh(new_rate)

        return {
            "created": len(new_rates),
            "created_by": user,
            "items": new_rates,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while bulk creating rates") from exc


@router.put("/{rate_id}")
def update_rate(
    rate_id: int,
    update: RateUpdate,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ensure_positive_rate(update.rate)

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


@router.patch("/{rate_id}")
def patch_rate(
    rate_id: int,
    patch: RatePatch,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if (
        patch.base_currency is None
        and patch.target_currency is None
        and patch.rate is None
        and patch.date is None
    ):
        raise HTTPException(status_code=422, detail="No fields provided to update")

    try:
        rate = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
        if not rate:
            raise HTTPException(status_code=404, detail="Rate not found")

        if patch.base_currency is not None:
            rate.base_currency = normalize_currency(patch.base_currency, "base_currency")
        if patch.target_currency is not None:
            rate.target_currency = normalize_currency(patch.target_currency, "target_currency")
        if patch.rate is not None:
            ensure_positive_rate(patch.rate)
            rate.rate = patch.rate
        if patch.date is not None:
            rate.date = patch.date

        db.commit()
        db.refresh(rate)
        return rate
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while patching rate") from exc


@router.delete("/bulk")
def delete_rates_bulk(
    payload: RateBulkDelete,
    admin_user: str = Depends(require_admin),
    db: Session = Depends(get_db),
):
    try:
        rates = db.query(ExchangeRate).filter(ExchangeRate.id.in_(payload.ids)).all()
        if not rates:
            raise HTTPException(status_code=404, detail="No matching rates found")

        found_ids = {rate.id for rate in rates}
        missing_ids = sorted(set(payload.ids) - found_ids)

        for rate in rates:
            db.delete(rate)
        db.commit()

        return {
            "deleted": len(rates),
            "missing_ids": missing_ids,
            "deleted_by": admin_user,
        }
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while bulk deleting rates") from exc


@router.delete("/{rate_id}")
def delete_rate(
    rate_id: int,
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        rate = db.query(ExchangeRate).filter(ExchangeRate.id == rate_id).first()
        if not rate:
            raise HTTPException(status_code=404, detail="Rate not found")

        db.delete(rate)
        db.commit()
        return {"message": "Rate deleted", "deleted_by": user}
    except HTTPException:
        raise
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error while deleting rate") from exc
