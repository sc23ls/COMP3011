from pydantic import BaseModel
from datetime import date


class RateCreate(BaseModel):

    base_currency: str
    target_currency: str
    rate: float
    date: date


class RateUpdate(BaseModel):

    rate: float