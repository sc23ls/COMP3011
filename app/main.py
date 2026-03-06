from fastapi import FastAPI
from app.database import engine, Base, SessionLocal
from app.models import currency, exchange_rate
from app.models.exchange_rate import ExchangeRate

app = FastAPI(title="Forex Analytics API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Forex Analytics API running"}


@app.get("/rates/count")
def rate_count():
    db = SessionLocal()
    count = db.query(ExchangeRate).count()
    db.close()
    return {"total_rates": count}