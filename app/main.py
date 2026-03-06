from fastapi import FastAPI
from app.database import engine, Base
from app.models import currency, exchange_rate

app = FastAPI(title="Forex Analytics API")

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "Forex Analytics API running"}