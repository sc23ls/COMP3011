from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine, get_db
from app.models.exchange_rate import ExchangeRate
from app.routers import conversion, analytics
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth
from app.routers import rates

app = FastAPI(title="Forex Analytics API")

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(conversion.router)
app.include_router(analytics.router)
app.include_router(auth.router)
app.include_router(rates.router)


@app.get("/")
def frontend():
    return FileResponse("frontend/index.html")


@app.get("/rates/count")
def rate_count(db: Session = Depends(get_db)):
    try:
        count = db.query(ExchangeRate).count()
        return {"total_rates": count}
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while counting rates") from exc

@app.get("/debug")
def debug_rates(db: Session = Depends(get_db)):
    try:
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

        return [
            {"date": r.date, "rate": r.rate}
            for r in rates
        ]
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Database error while reading debug rates") from exc
    
