from fastapi import APIRouter
from app.database import SessionLocal
from app.analytics.volatility import calculate_volatility

router = APIRouter()


@router.get("/volatility")
def get_volatility(base: str, target: str):

    db = SessionLocal()

    vol = calculate_volatility(db, base, target)

    db.close()

    if vol is None:
        return {"error": "Not enough data"}

    return {
        "base": base,
        "target": target,
        "volatility": round(vol, 6)
    }