from fastapi import APIRouter
from app.database import SessionLocal
from app.analytics.volatility import calculate_volatility
from app.analytics.trend import detect_trend
from app.analytics.regime import detect_regime


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

@router.get("/trend")
def get_trend(base: str, target: str):

    db = SessionLocal()

    trend = detect_trend(db, base, target)

    db.close()

    return {
        "base": base,
        "target": target,
        "trend": trend
    }

@router.get("/regime")
def get_regime(base: str, target: str):

    db = SessionLocal()

    result = detect_regime(db, base, target)

    db.close()

    if result is None:
        return {"error": "Insufficient data"}

    return {
        "base": base,
        "target": target,
        "trend": result["trend"],
        "volatility": round(result["volatility"], 6),
        "regime": result["regime"]
    }