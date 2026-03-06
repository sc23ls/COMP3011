from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.models import currency, exchange_rate
from app.models.exchange_rate import ExchangeRate
from app.routers import conversion, analytics

app = FastAPI(title="Forex Analytics API")

Base.metadata.create_all(bind=engine)

app.include_router(conversion.router)
app.include_router(analytics.router)

@app.get("/")
def root():
    return {"message": "Forex Analytics API running"}


@app.get("/rates/count")
def rate_count():
    db = SessionLocal()
    count = db.query(ExchangeRate).count()
    db.close()
    return {"total_rates": count}

@app.get("/debug")
def debug_rates():
    db = SessionLocal()

    rates = (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency == "EUR",
            ExchangeRate.target_currency == "USD"
        )
        .order_by(ExchangeRate.date.desc())
        .limit(5)
        .all()
    )

    db.close()

    return [
        {"date": r.date, "rate": r.rate}
        for r in rates
    ]